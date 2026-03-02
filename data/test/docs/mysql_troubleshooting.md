# MySQL Troubleshooting Guide

## Common Issues

### Connection Pool Exhaustion
- **Symptoms**: "Too many connections" error
- **Possible Causes**:
  1. Slow queries holding connections
  2. Connection leaks in application
  3. max_connections too low
  4. Long-running transactions
- **Solution**:
  1. Kill slow queries: `SHOW PROCESSLIST`
  2. Check for slow queries: `SHOW FULL PROCESSLIST`
  3. Increase max_connections temporarily
  4. Fix application connection pool settings

### Slow Queries
- **Symptoms**: Query execution > threshold (usually 1s)
- **Solution**:
  1. Enable slow query log
  2. Use EXPLAIN to analyze query plan
  3. Add missing indexes
  4. Optimize query structure
  5. Consider query cache or read replicas

### Replication Lag
- **Symptoms**: Slave behind master
- **Solution**:
  1. Check replication status: `SHOW SLAVE STATUS`
  2. Reduce write load on master
  3. Optimize slave hardware
  4. Consider parallel replication
