import streamlit as st
import time
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx
from queue import Queue
from threading import Thread
import random

# Initialize session state variables if they don't exist
if "queue" not in st.session_state:
    st.session_state.queue = Queue()
if "running" not in st.session_state:
    st.session_state.running = False
if "messages" not in st.session_state:
    st.session_state.messages = []


def producer(
    queue,
):
    """Produces random numbers and adds them to the queue"""
    while st.session_state.running:
        if queue.qsize() < 10:  # Limit queue size
            number = random.randint(1, 100)
            queue.put(number)
            st.session_state.messages.append(f"Produced: {number}")
            time.sleep(1)  # Simulate work


def consumer(
    queue,
):
    """Consumes numbers from the queue and processes them"""
    while st.session_state.running:
        if not queue.empty():
            number = queue.get()
            processed = number * 2  # Simple processing
            st.session_state.messages.append(
                f"Consumed: {number} → Processed: {processed}"
            )
            time.sleep(2)  # Simulate work
            queue.task_done()


st.title("Producer-Consumer Demo")

# Start/Stop button
if st.button("Start" if not st.session_state.running else "Stop"):
    st.session_state.running = not st.session_state.running

    if st.session_state.running:
        # Clear previous messages when starting new session
        st.session_state.messages = []

        # Start producer and consumer threads
        producer_thread = Thread(target=producer, args=(st.session_state.queue,))
        consumer_thread = Thread(target=consumer, args=(st.session_state.queue,))
        add_script_run_ctx(producer_thread)
        add_script_run_ctx(consumer_thread)
        producer_thread.daemon = True
        consumer_thread.daemon = True

        producer_thread.start()
        consumer_thread.start()

# Display queue status
st.subheader("Queue Status")
st.write(f"Current queue size: {st.session_state.queue.qsize()}")
log_placeholder = st.empty()

# Create a container for the queue size
queue_size_placeholder = st.empty()
# Display messages
while True:

    # Update queue size
    queue_size_placeholder.subheader("Queue Status")
    queue_size_placeholder.write(
        f"Current queue size: {st.session_state.queue.qsize()}"
    )

    # Update activity log
    with log_placeholder.container():
        st.subheader("Activity Log")
        for msg in reversed(st.session_state.messages[-10:]):
            st.text(msg)

    time.sleep(0.1)  # Update eve