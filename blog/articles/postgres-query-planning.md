# How PostgreSQL Query Planning Actually Works

**Date:** October 2023
**Category:** Data Engineering

---

If you have ever stared at a slow query, ran `EXPLAIN`, and nodded pretending to understand why Postgres chose a Sequential Scan over your perfectly good Index, this article is for you.

Understanding the query optimizer is the single most important skill for high-performance database engineering. It is not magic; it is a cost-based algorithm that makes statistically driven decisions. When it fails, it usually isn't because the optimizer is "dumb", but because its cost model or statistics do not align with reality.

In this deep dive, we will walk through the internal machinery of the Postgres planner, dissect the cost model, and analyze real execution plans.

## The Life of a Query

Before we get to planning, let's contextualize where it fits in the lifecycle of a query.

```text
+----------------+      +----------------+      +----------------+
|  SQL Query     | ---> |     Parser     | ---> |   Parse Tree   |
+----------------+      +----------------+      +----------------+
                                                       |
                                                       v
+----------------+      +----------------+      +----------------+
|    Executor    | <--- |    Planner     | <--- |    Rewriter    |
+----------------+      +----------------+      +----------------+
        |
        v
    Results
```

1.  **Parser**: Checks syntax and builds a parse tree.
2.  **Rewriter**: Applies rules (like Views) to modify the tree.
3.  **Planner**: The brain. It generates multiple valid execution paths (plans), estimates the cost of each, and picks the cheapest one.
4.  **Executor**: Runs the chosen plan.

Our focus is step 3. The Planner is essentially solving a combinatorial optimization problem. For a simple `SELECT * FROM table`, there is effectively one path. But join 5 tables, add standard filters, and you suddenly have thousands of possible join orders and access methods.

## The Cost Model

Postgres uses a **Cost-Based Optimizer (CBO)**. It doesn't pick the "fastest" plan; it picks the plan with the lowest arbitrary *cost units*.

These units are defined in `postgresql.conf`. The base unit is `seq_page_cost`, which is arbitrarily set to **1.0**. All other costs are relative to this.

| Parameter | Default | Meaning |
| :--- | :--- | :--- |
| `seq_page_cost` | 1.0 | Cost to fetch a disk page sequentially. |
| `random_page_cost` | 4.0 | Cost to fetch a disk page randomly. |
| `cpu_tuple_cost` | 0.01 | Cost to process a single row (CPU). |
| `cpu_index_tuple_cost` | 0.005 | Cost to process an index entry. |
| `cpu_operator_cost` | 0.0025 | Cost to perform an operation (e.g., `+` or `=`). |

### The "SSD" Adjustment
The default `random_page_cost` of 4.0 assumes mechanical spinning disks (HDD), where seeking is expensive. On modern cloud SSDs (gp3, io2), random seeks are almost as cheap as sequential ones.

**Pro Tip:** If your indexes aren't being used, try lowering `random_page_cost` to **1.1** or **1.2**. This tells the planner that random seeks are cheap, making Index Scans more attractive.

```sql
-- Check your current settings
SHOW random_page_cost;
SHOW seq_page_cost;
```

## Access Methods: Getting the Data

The planner's first job is to figure out how to pull data from individual tables.

### 1. Sequential Scan (`Seq Scan`)
The brute force method. Read the table from beginning to end.
*   **When it's used:** Small tables, or when fetching a large % of rows.
*   **Cost Formula:** `(pages * seq_page_cost) + (rows * cpu_tuple_cost)`

### 2. Index Scan (`Index Scan`)
Traverse the B-Tree to find Row IDs (CTIDs), then fetch the actual data pages.
*   **When it's used:** High cardinality lookups (searching for a specific email or ID).
*   **The Catch:** It involves random I/O. If you need to fetch 50% of the table, jumping around randomly is slower than just reading the whole file sequentially.

### 3. Index Only Scan
A special case where *all* requested columns are in the index itself. Postgres doesn't need to visit the main table (Heap) at all... *mostly*.
*   **The "Visibility Map" Caveat:** Postgres uses MVCC. It must verify that the index entry is "visible" to your transaction. It checks the Visibility Map. If the page isn't marked "all visible", it *must* check the heap, degrading performance.

### 4. Bitmap Heap Scan
A hybrid approach.
1.  **Bitmap Index Scan:** Scans the index and builds a bitmap of pages that need to be visited.
2.  **Bitmap Heap Scan:** Reads those pages in sequential order.
*   **Benefit:** Avoids random I/O thrashing while still using the index.

## Join Strategies: Putting It Together

Once the planner knows how to get data, it must join it.

### Nested Loop Join
The simple double for-loop.
```python
for outer_row in outer_table:
    for inner_row in inner_table:
        if match(outer_row, inner_row):
            yield (outer_row, inner_row)
```
*   **Best for:** Small datasets or when the inner table is indexed on the join key.
*   **Complexity:** O(N * M) (worst case), or O(N * log M) with an index.

### Hash Join
Builds a hash table in memory from the smaller table, then scans the larger table and probes the hash.
*   **Best for:** Large, unsorted datasets. Equality joins only (`=`).
*   **Complexity:** O(N + M).
*   **Memory Limit:** Limited by `work_mem`. If the hash table doesn't fit in memory, it spills to disk, killing performance.

### Merge Join
Sorts both tables on the join key, then zips them together.
*   **Best for:** Very large tables that are already sorted (or cheap to sort).
*   **Complexity:** O(N log N + M log M) (for sorting).

## Dissecting an EXPLAIN ANALYZE

Let's look at a realistic scenario. We have a `orders` table (1M rows) and a `users` table (100k rows).

Query:
```sql
EXPLAIN ANALYZE
SELECT u.email, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.created_at > NOW() - INTERVAL '1 day';
```

**Output:**
```text
Hash Join  (cost=2500.00..15000.00 rows=500 width=40) (actual time=15.000..45.000 rows=450 loops=1)
  Hash Cond: (o.user_id = u.id)
  ->  Seq Scan on orders o  (cost=0.00..12000.00 rows=5000 width=12) (actual time=0.010..25.000 rows=5000 loops=1)
        Filter: (created_at > (now() - '1 day'::interval))
        Rows Removed by Filter: 995000
  ->  Hash  (cost=2000.00..2000.00 rows=100000 width=32) (actual time=10.000..10.000 rows=100000 loops=1)
        Buckets: 131072  Batches: 1  Memory Usage: 6000kB
        ->  Seq Scan on users u  (cost=0.00..2000.00 rows=100000 width=32) (actual time=0.005..8.000 rows=100000 loops=1)
```

### Analysis
1.  **Bottom Up:** The plan starts at the leaves (Seq Scans).
2.  **`Seq Scan on users`:** It read all 100k users. Cost was 2000.
3.  **`Hash`:** It built a hash table of users. Memory Usage was 6MB. This fits comfortably in `work_mem` (default is 4MB, assume we bumped it).
4.  **`Seq Scan on orders`:** It scanned the orders table. Notice `Rows Removed by Filter: 995000`. This is painful. We scanned 1M rows to find 5000 recent ones.
    *   **Optimization Opportunity:** An index on `orders(created_at)` would turn this `Seq Scan` into an `Index Scan` or `Bitmap Heap Scan`.
5.  **`Hash Join`:** It probed the user hash table for each of the 5000 orders.

## Statistics: The Planner's Map

How did the planner guess `rows=5000` for the orders scan? Statistics.
Postgres maintains a histogram and most common values (MCV) list for every column in `pg_statistic`.

The **Auto-Vacuum** daemon is responsible for updating these stats. If you disable autovacuum, statistics get stale, and the planner starts making terrible decisions (like Nested Looping two massive tables).

## Conclusion

Query optimization is not about guessing. It's about:
1.  **Reading the Plan:** Understand `EXPLAIN (ANALYZE, BUFFERS)`.
2.  **Understanding Costs:** Know your `random_page_cost`.
3.  **Checking Stats:** Ensure autovacuum is healthy.
4.  **Indexing Wisely:** Indexes speed up reads but slow down writes.

Next time your query hangs, don't just add an index blindly. Ask the planner *why* it chose that path. The answer is usually in the costs.
