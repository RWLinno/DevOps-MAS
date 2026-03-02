# Kafka Troubleshooting Guide

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
