import harvester
import usecases.announcement
import usecases.announcement

h = harvester.Harvester()
h.login()
p = h.get_page()
b = h.get_boxes(p)
df, images_lists = h.harvest_links(b)

for _, (row, images) in enumerate(zip(df.to_dict(orient='records'), images_lists)):
    usecases.announcement.upsert(row, images)