# Redis Troubleshooting Guide

## Common Issues

### Connection Refused
- **Symptoms**: `Connection refused` errors in client logs
- **Possible Causes**:
  1. Redis server not running
  2. Firewall blocking port 6379
  3. Max connections reached
  4. OOM kill by system
- **Solution**:
  1. Check Redis process: `redis-cli ping`
  2. Check system logs: `journalctl -u redis`
  3. Check memory: `redis-cli info memory`
  4. Restart if needed: `systemctl restart redis`

### High Latency
- **Symptoms**: p99 latency > 500ms
- **Possible Causes**:
  1. Memory pressure (swapping)
  2. Large key operations (KEYS *, SMEMBERS on large sets)
  3. Lua script execution
  4. Network issues
- **Solution**:
  1. Check slow log: `redis-cli slowlog get 10`
  2. Optimize data structures
  3. Use SCAN instead of KEYS
  4. Monitor with `redis-cli --latency`

### Memory Issues
- **Symptoms**: `maxmemory` reached, eviction happening
- **Solution**:
  1. Check memory: `redis-cli info memory`
  2. Analyze key distribution: `redis-cli --bigkeys`
  3. Set appropriate TTL on keys
  4. Consider Redis Cluster for horizontal scaling
