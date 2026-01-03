import pika

def seed_urls():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    channel.queue_declare(queue="url_queue", durable=True)

    seed_urls = [
        "https://en.wikipedia.org/wiki/Infosys"
    ]

    for url in seed_urls:
        channel.basic_publish(
            exchange="",
            routing_key="url_queue",
            body=url.encode()
        )
        print(f"[PRODUCER] Sent: {url}")

    connection.close()


if __name__ == "__main__":
    seed_urls()
