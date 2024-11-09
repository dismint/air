import matplotlib.pyplot as plt
import urllib.request
import datetime
import csv
import os


# utiliy function for clearing carriage return

def clear():
    spaces = " " * 100
    print(f"\r{spaces}\r", end="")

# generate datetime points for the last 24 hours

now = datetime.datetime.now()
dates = [now - datetime.timedelta(hours=i) for i in range(24)]

print("\rStarting Download...", end="")

date_to_quality = {}

for i, date in enumerate(dates):
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    hour = date.strftime("%H")
    ymd = year + month + day


    url = f"https://s3-us-west-1.amazonaws.com//files.airnowtech.org/airnow/{year}/{ymd}/HourlyAQObs_{ymd}{hour}.dat"
    urllib.request.urlretrieve(url, f"{ymd}{hour}.dat")

    # default quality to -1, we will check later to deal with cases where data was not present in the downloaded dataset
    key = f"{year}-{month}-{day}:{hour}"
    date_to_quality[key] = -1

    with open(f"{ymd}{hour}.dat") as f:
        data = list(csv.reader(f.read().split("\n")))
        for l in data[1:]:
            # skip blank rows
            if not l:
                continue

            # match row
            if l[1] == "BOSTON-KENMORE":
                date_to_quality[key] = float(l[16])
                break

    # cleanup
    urllib.request.urlcleanup()
    os.remove(f"{ymd}{hour}.dat")

    clear()
    print(f"\r{i} / 24 -- {int(i/24 * 100)} %", end="")

clear()
print("Download Complete!")

# parse to make sure that any days without data are ommitted from the plot

date_to_quality = {k: v for k, v in date_to_quality.items() if v != -1}
# turn into list to preserver order, sort by date
date_to_quality = [(k, v) for k, v in date_to_quality.items()]
date_to_quality.sort()

# plot the data

plt.plot([i[0] for i in date_to_quality], [i[1] for i in date_to_quality])
plt.xticks(rotation=35)

# save plot as png

plt.savefig("plot.png", bbox_inches="tight")

