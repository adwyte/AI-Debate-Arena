from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_argument(data):
    producer.send('debate.input', data)
    producer.flush()
    print("Message sent:", data)