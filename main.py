import harvester
import usecases.announcement
import usecases.announcement
import signal

# THREAD_COUNT = 2

harvester = harvester.Harvester()
harvester.login()
harvester.hash_list = usecases.announcement.load_id_set()
# thread_stop_event = threading.Event()
#
# def thread_runner():
#     while not thread_stop_event.is_set():
#         p = harvester.get_page()
#         b = harvester.get_boxes(p)
#         df, images_lists = harvester.harvest_links(b)
#
#         for (row, images) in zip(df.to_dict(orient='records'), images_lists):
#             usecases.announcement.upsert(row, images)
#
#
# def thread_stop(signum, frame):
#     print("thread stopped")
#     harvester.stop_event.set()
#     thread_stop_event.set()
#
# if __name__ == '__main__':
#     threads = []
#     signal.signal(signal.SIGINT, thread_stop)
#
#     for _ in range(THREAD_COUNT):
#         thread = threading.Thread(target=thread_runner, daemon=True)
#         thread.start()
#         threads.append(thread)
#
#     for thread in threads:
#         thread.join()

if __name__ == '__main__':
    running = True


    def handle_sigint(signum, frame):
        global running, harvester
        print("Termination signal received. Exiting gracefully...")
        running = False
        harvester.stop_event.set()


    signal.signal(signal.SIGINT, handle_sigint)

    try:
        while running:
            p = harvester.get_page()
            b = harvester.get_boxes(p)
            df, images_lists = harvester.harvest_links(b)

            for (row, images) in zip(df.to_dict(orient='records'), images_lists):
                usecases.announcement.upsert(row, images)

            usecases.announcement.commit_all()
    finally:
        print("Cleaning up resources...")
