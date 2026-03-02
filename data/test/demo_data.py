"""
Demo Data Generator
Creates realistic test data for demonstrating the full DevOps-MAS workflow.
Generates: log files, case records, knowledge documents, SFT samples, images.
"""

import json
import os
import random
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent


def generate_test_logs():
    """Generate realistic error logs for demo."""
    logs_dir = BASE_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)

    redis_log = """2025-12-15 08:23:01.234 [ERROR] redis.connection - Connection refused: 10.0.1.52:6379 (attempt 1/3)
2025-12-15 08:23:01.456 [WARN] redis.pool - Pool exhausted, waiting for available connection (max=50, active=50)
2025-12-15 08:23:02.789 [ERROR] redis.connection - Connection refused: 10.0.1.52:6379 (attempt 2/3)
2025-12-15 08:23:03.012 [ERROR] redis.connection - Connection refused: 10.0.1.52:6379 (attempt 3/3)
2025-12-15 08:23:03.234 [FATAL] redis.client - All connection attempts failed for node redis-cluster-03
2025-12-15 08:23:03.456 [ERROR] cache.service - CacheService unavailable, falling back to DB direct query
2025-12-15 08:23:04.789 [WARN] api.recommendation - Recommendation API latency spike: p99=2340ms (threshold: 500ms)
2025-12-15 08:23:05.012 [ERROR] api.recommendation - Request timeout after 3000ms for user_id=U87654321
2025-12-15 08:23:06.234 [INFO] monitor.alert - Alert triggered: redis_connection_failure (severity=P1)
2025-12-15 08:23:07.456 [INFO] oncall.pager - Paging on-call engineer: william.ruan@example.com
2025-12-15 08:23:10.789 [INFO] redis.recovery - Attempting reconnection to redis-cluster-03...
2025-12-15 08:23:15.012 [INFO] redis.recovery - Connection restored to 10.0.1.52:6379
2025-12-15 08:23:15.234 [INFO] cache.service - CacheService restored, flushing stale cache entries
2025-12-15 08:23:16.456 [INFO] api.recommendation - Latency normalized: p99=120ms"""

    kafka_log = """2025-12-16 14:05:22.111 [WARN] kafka.consumer - Consumer group rebalancing triggered (group=data-pipeline-cg)
2025-12-16 14:05:23.222 [ERROR] kafka.consumer - Failed to commit offset for topic=user-events, partition=7, offset=1234567
2025-12-16 14:05:24.333 [ERROR] kafka.consumer - Consumer lag exceeded threshold: topic=user-events, partition=7, lag=50000
2025-12-16 14:05:25.444 [WARN] kafka.producer - Producer buffer full, blocking for 5000ms (topic=processed-events)
2025-12-16 14:05:30.555 [ERROR] pipeline.transform - Data transformation failed: NullPointerException at EventProcessor.java:142
2025-12-16 14:05:31.666 [ERROR] pipeline.transform - Stack trace: java.lang.NullPointerException
    at com.example.pipeline.EventProcessor.processEvent(EventProcessor.java:142)
    at com.example.pipeline.PipelineRunner.run(PipelineRunner.java:89)
    at com.example.pipeline.Main.main(Main.java:23)
2025-12-16 14:05:32.777 [WARN] kafka.consumer - Messages accumulating in DLQ: topic=user-events-dlq, count=1523
2025-12-16 14:05:33.888 [INFO] monitor.alert - Alert triggered: kafka_consumer_lag_high (severity=P1)
2025-12-16 14:06:00.999 [INFO] kafka.consumer - Rebalance complete, partitions reassigned"""

    mysql_log = """2025-12-17 22:15:01.100 [ERROR] mysql.connection - Too many connections (max=500, current=500)
2025-12-17 22:15:02.200 [ERROR] mysql.query - Query timeout after 30s: SELECT * FROM orders WHERE created_at > '2025-12-01' AND status IN ('pending', 'processing') ORDER BY created_at DESC
2025-12-17 22:15:03.300 [WARN] mysql.slow_query - Slow query detected (12.5s): Full table scan on orders (rows_examined=2,847,392)
2025-12-17 22:15:04.400 [ERROR] mysql.replication - Replication lag: master=binlog.000142:4567890, slave=binlog.000142:4567000 (lag=890 events, ~15s)
2025-12-17 22:15:05.500 [WARN] mysql.innodb - InnoDB buffer pool hit rate: 85% (below 95% threshold)
2025-12-17 22:15:06.600 [INFO] mysql.optimizer - Missing index suggestion: CREATE INDEX idx_orders_status_created ON orders(status, created_at)
2025-12-17 22:15:07.700 [ERROR] api.order - OrderService: database connection pool exhausted, request queued
2025-12-17 22:15:08.800 [INFO] monitor.alert - Alert triggered: mysql_connection_exhausted (severity=P0)"""

    with open(logs_dir / "redis_error.log", "w") as f:
        f.write(redis_log)
    with open(logs_dir / "kafka_error.log", "w") as f:
        f.write(kafka_log)
    with open(logs_dir / "mysql_error.log", "w") as f:
        f.write(mysql_log)

    print(f"Generated {3} test log files in {logs_dir}")


def generate_test_cases():
    """Generate sample incident cases."""
    cases_dir = BASE_DIR / "cases"
    cases_dir.mkdir(exist_ok=True)

    cases = [
        {
            "case_id": "OC-A1B2C3",
            "title": "Redis Cluster Node Failure Causing Recommendation API Timeout",
            "description": "Recommendation API p99 latency spiked to 2340ms. Root cause traced to redis-cluster-03 node failure.",
            "status": "resolved",
            "priority": "P1",
            "created_at": time.time() - 86400 * 3,
            "updated_at": time.time() - 86400 * 3 + 1800,
            "resolved_at": time.time() - 86400 * 3 + 1800,
            "root_cause": "Redis cluster node redis-cluster-03 (10.0.1.52) experienced OOM kill due to memory leak in Lua script execution. Connection pool was exhausted (50/50).",
            "solution": "1. Restarted redis-cluster-03 node\n2. Increased maxmemory from 4GB to 8GB\n3. Fixed Lua script memory leak\n4. Added connection pool monitoring alert",
            "tags": ["redis", "timeout", "cache", "recommendation", "P1"],
            "related_logs": ["data/test/logs/redis_error.log"],
            "events": [
                {"timestamp": time.time() - 86400 * 3, "event_type": "created", "content": "Alert triggered: redis_connection_failure"},
                {"timestamp": time.time() - 86400 * 3 + 120, "event_type": "message", "content": "DevOps-MAS analyzed logs and identified redis-cluster-03 as the failing node", "agent_name": "log_analysis_agent"},
                {"timestamp": time.time() - 86400 * 3 + 300, "event_type": "diagnosis", "content": "Root cause: OOM kill on redis-cluster-03 due to Lua script memory leak", "agent_name": "comprehensive_agent"},
                {"timestamp": time.time() - 86400 * 3 + 1200, "event_type": "resolution", "content": "Node restarted, maxmemory increased, Lua script fixed", "agent_name": "knowledge_agent"},
                {"timestamp": time.time() - 86400 * 3 + 1800, "event_type": "status_change", "content": "Case resolved"},
            ],
            "metadata": {"resolution_time_min": 30, "affected_users": 15000}
        },
        {
            "case_id": "OC-D4E5F6",
            "title": "Kafka Consumer Lag Causing Data Pipeline Delay",
            "description": "Data pipeline consumer lag exceeded 50K messages on user-events topic partition 7.",
            "status": "resolved",
            "priority": "P1",
            "created_at": time.time() - 86400 * 2,
            "updated_at": time.time() - 86400 * 2 + 3600,
            "resolved_at": time.time() - 86400 * 2 + 3600,
            "root_cause": "NullPointerException in EventProcessor.java:142 caused consumer to repeatedly fail and rebalance. Dead letter queue accumulated 1523 messages.",
            "solution": "1. Fixed NPE in EventProcessor with null check\n2. Replayed DLQ messages\n3. Added input validation in pipeline\n4. Increased consumer group parallelism from 3 to 6",
            "tags": ["kafka", "consumer-lag", "pipeline", "NPE", "P1"],
            "related_logs": ["data/test/logs/kafka_error.log"],
            "events": [
                {"timestamp": time.time() - 86400 * 2, "event_type": "created", "content": "Alert: kafka_consumer_lag_high"},
                {"timestamp": time.time() - 86400 * 2 + 600, "event_type": "message", "content": "Log analysis found NPE in EventProcessor.java:142", "agent_name": "log_analysis_agent"},
                {"timestamp": time.time() - 86400 * 2 + 1200, "event_type": "diagnosis", "content": "NPE causing consumer rebalance loop", "agent_name": "log_analysis_agent"},
                {"timestamp": time.time() - 86400 * 2 + 3600, "event_type": "resolution", "content": "NPE fixed, DLQ replayed, parallelism increased"},
            ],
            "metadata": {"resolution_time_min": 60, "affected_services": ["data-pipeline", "recommendation"]}
        },
        {
            "case_id": "OC-G7H8I9",
            "title": "MySQL Connection Pool Exhaustion on Order Service",
            "description": "Order service unable to acquire database connections. All 500 connections consumed.",
            "status": "resolved",
            "priority": "P0",
            "created_at": time.time() - 86400,
            "updated_at": time.time() - 86400 + 2700,
            "resolved_at": time.time() - 86400 + 2700,
            "root_cause": "Slow query (full table scan on orders table, 2.8M rows) holding connections for 12+ seconds. Missing index on (status, created_at) columns.",
            "solution": "1. Killed long-running queries\n2. Added index: CREATE INDEX idx_orders_status_created ON orders(status, created_at)\n3. Increased max_connections to 800 temporarily\n4. Implemented query timeout at application level (5s)\n5. Added slow query alert threshold",
            "tags": ["mysql", "connection-pool", "slow-query", "index", "P0"],
            "related_logs": ["data/test/logs/mysql_error.log"],
            "events": [
                {"timestamp": time.time() - 86400, "event_type": "created", "content": "P0 Alert: mysql_connection_exhausted"},
                {"timestamp": time.time() - 86400 + 180, "event_type": "message", "content": "Immediate: Killed 23 long-running queries", "agent_name": "comprehensive_agent"},
                {"timestamp": time.time() - 86400 + 600, "event_type": "diagnosis", "content": "Missing index causing full table scan on orders", "agent_name": "log_analysis_agent"},
                {"timestamp": time.time() - 86400 + 1800, "event_type": "message", "content": "Index created, connections normalizing"},
                {"timestamp": time.time() - 86400 + 2700, "event_type": "resolution", "content": "All fixes applied, monitoring stable for 15min"},
            ],
            "metadata": {"resolution_time_min": 45, "revenue_impact": "$12,000"}
        },
        {
            "case_id": "OC-J1K2L3",
            "title": "API Gateway Certificate Expiration Warning",
            "description": "SSL certificate for api.example.com expiring in 7 days. Needs renewal before expiration.",
            "status": "open",
            "priority": "P2",
            "created_at": time.time() - 3600,
            "updated_at": time.time() - 3600,
            "resolved_at": None,
            "root_cause": None,
            "solution": None,
            "tags": ["ssl", "certificate", "api-gateway", "maintenance", "P2"],
            "related_logs": [],
            "events": [
                {"timestamp": time.time() - 3600, "event_type": "created", "content": "Certificate expiration warning: api.example.com expires in 7 days"},
            ],
            "metadata": {"cert_expiry": "2026-03-07", "domain": "api.example.com"}
        },
    ]

    for case in cases:
        path = cases_dir / f"{case['case_id']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(case, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(cases)} test cases in {cases_dir}")


def generate_test_documents():
    """Generate knowledge base documents."""
    docs_dir = BASE_DIR / "docs"
    docs_dir.mkdir(exist_ok=True)

    redis_doc = """# Redis Troubleshooting Guide

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
"""

    kafka_doc = """# Kafka Troubleshooting Guide

## Common Issues

### Consumer Lag
- **Symptoms**: Consumer lag > threshold, data processing delayed
- **Possible Causes**:
  1. Slow consumer processing
  2. Consumer rebalancing
  3. Insufficient consumer instances
  4. Uneven partition distribution
- **Solution**:
  1. Check consumer lag: `kafka-consumer-groups --describe --group <group>`
  2. Increase consumer parallelism
  3. Optimize message processing logic
  4. Check for poison messages in DLQ

### Producer Failures
- **Symptoms**: Messages not being produced, buffer full errors
- **Possible Causes**:
  1. Broker unavailable
  2. Topic does not exist
  3. Producer buffer full
  4. Serialization errors
- **Solution**:
  1. Check broker health: `kafka-broker-api-versions`
  2. Verify topic exists: `kafka-topics --list`
  3. Increase buffer.memory or batch.size
  4. Review serializer configuration
"""

    mysql_doc = """# MySQL Troubleshooting Guide

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
"""

    with open(docs_dir / "redis_troubleshooting.md", "w") as f:
        f.write(redis_doc)
    with open(docs_dir / "kafka_troubleshooting.md", "w") as f:
        f.write(kafka_doc)
    with open(docs_dir / "mysql_troubleshooting.md", "w") as f:
        f.write(mysql_doc)

    print(f"Generated {3} knowledge base documents in {docs_dir}")


def generate_sft_samples():
    """Generate sample SFT training data."""
    sft_dir = BASE_DIR.parent / "sft"
    sft_dir.mkdir(exist_ok=True)

    samples = [
        {
            "instruction": "Redis connection refused, recommendation API latency spiked to 2300ms. How to diagnose?",
            "input": "Error log shows: Connection refused: 10.0.1.52:6379, Pool exhausted (50/50)",
            "output": "## Diagnosis Steps\n\n1. **Check Redis Node Status**: SSH to 10.0.1.52 and verify Redis process\n   ```bash\n   redis-cli -h 10.0.1.52 -p 6379 ping\n   systemctl status redis\n   ```\n\n2. **Check System Resources**: The node might be OOM killed\n   ```bash\n   dmesg | grep -i oom\n   free -h\n   ```\n\n3. **Connection Pool Analysis**: Pool exhausted (50/50) means all connections are in use\n   - Check for connection leaks in application\n   - Verify connection timeout settings\n\n4. **Immediate Mitigation**:\n   - Restart Redis node if down\n   - Enable fallback to direct DB queries\n   - Page infrastructure team for cluster health check\n\n## Root Cause: Likely OOM kill or network partition affecting redis-cluster-03."
        },
        {
            "instruction": "Kafka consumer lag exceeding 50K messages. What should I check?",
            "input": "Topic: user-events, Partition: 7, Consumer group: data-pipeline-cg",
            "output": "## Investigation Steps\n\n1. **Check Consumer Status**:\n   ```bash\n   kafka-consumer-groups --bootstrap-server kafka:9092 --describe --group data-pipeline-cg\n   ```\n\n2. **Check for Error Messages**: Look for exceptions in consumer application logs\n   - NullPointerException, SerializationException, etc.\n   - Check Dead Letter Queue (DLQ) for accumulated messages\n\n3. **Check Consumer Group Rebalancing**: Frequent rebalancing can cause lag\n   - Review consumer heartbeat and session timeout settings\n   - Check if consumers are being killed/restarted\n\n4. **Performance Analysis**:\n   - Monitor consumer processing time per message\n   - Check downstream service latency\n\n5. **Quick Fix**:\n   - Increase consumer instances if processing is slow\n   - If a specific partition is lagged, check for hot key issues\n   - Reset consumer offset if messages are stale"
        },
        {
            "instruction": "MySQL shows 'Too many connections' error. Order service is down.",
            "input": "max_connections=500, current=500. Slow query log shows full table scan on orders table.",
            "output": "## Immediate Actions (P0 Response)\n\n1. **Kill Long-Running Queries**:\n   ```sql\n   SHOW FULL PROCESSLIST;\n   -- Kill queries running > 10s\n   SELECT CONCAT('KILL ', id, ';') FROM information_schema.processlist WHERE time > 10;\n   ```\n\n2. **Temporary Relief**:\n   ```sql\n   SET GLOBAL max_connections = 800;\n   ```\n\n3. **Root Cause Fix - Add Missing Index**:\n   ```sql\n   CREATE INDEX idx_orders_status_created ON orders(status, created_at);\n   ```\n\n4. **Application-Level Fix**:\n   - Add query timeout (5s max)\n   - Implement connection pool sizing (min=10, max=50 per service)\n   - Add circuit breaker for DB calls\n\n5. **Prevention**:\n   - Enable slow query log with 1s threshold\n   - Set up alerts for connection count > 80%\n   - Regular index optimization reviews"
        },
        {
            "instruction": "How to set up monitoring alerts for Redis cluster?",
            "input": "",
            "output": "## Redis Monitoring Alert Setup\n\n### Key Metrics to Monitor\n\n1. **Connection Metrics**:\n   - `connected_clients` - Alert if > 80% of maxclients\n   - `rejected_connections` - Alert on any increase\n   - `blocked_clients` - Alert if > 0 for > 30s\n\n2. **Memory Metrics**:\n   - `used_memory` / `maxmemory` - Alert if > 85%\n   - `mem_fragmentation_ratio` - Alert if > 1.5 or < 1.0\n\n3. **Performance Metrics**:\n   - `instantaneous_ops_per_sec` - Baseline + anomaly detection\n   - `keyspace_hits` / (`keyspace_hits` + `keyspace_misses`) - Alert if < 90%\n\n4. **Replication**:\n   - `master_link_status` - Alert if not 'up'\n   - `master_last_io_seconds_ago` - Alert if > 10\n\n### Prometheus + Grafana Setup\n```yaml\n# prometheus.yml\nscrape_configs:\n  - job_name: 'redis'\n    static_configs:\n      - targets: ['redis-exporter:9121']\n```"
        },
    ]

    output_path = sft_dir / "sft_dataset_alpaca.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(samples)} SFT samples in {output_path}")


def generate_all():
    """Generate all test data."""
    print("=== Generating DevOps-MAS Demo Data ===\n")
    generate_test_logs()
    generate_test_cases()
    generate_test_documents()
    generate_sft_samples()
    print("\n=== All demo data generated successfully ===")


if __name__ == "__main__":
    generate_all()
