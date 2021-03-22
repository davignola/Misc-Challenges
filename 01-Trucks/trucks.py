#!/usr/bin/python3
import os
import sys
import time
from math import ceil

START_TIME = time.time()

# Base L/100km
BASE_CONSUMP = 18
# Modifiers
FLAT_FACTOR = 0
HIGH_FACTOR = 0.2
LOW_FACTOR = -0.1
# Added after above
LOADED_FACTOR = 0.07
UNLOADED_FACTOR = 0.04

STARTING_FUEL = 200
BARREL_FUEL = 15

# Pre-calculations
flatAddition = BASE_CONSUMP * FLAT_FACTOR
highAddition = BASE_CONSUMP * HIGH_FACTOR
lowAddition = BASE_CONSUMP * LOW_FACTOR


def isValid(x: str):
    "Check if the argument is a valid route data"
    return x == 'B' or x == 'H' or x == 'N'


def getConsumption(step: str, isLoaded: bool):
    "Calculate cunsumption for a specific step"
    stepConsumption = 0
    if step == 'H':
        stepConsumption = BASE_CONSUMP + highAddition
    elif step == 'B':
        stepConsumption = BASE_CONSUMP + lowAddition
    elif step == 'N':
        stepConsumption = BASE_CONSUMP + flatAddition

    return stepConsumption + (stepConsumption * (LOADED_FACTOR if isLoaded else UNLOADED_FACTOR))


def flipStep(step: str):
    "Flip the step dirrection for the return travel"
    if step == 'H':
        return 'B'
    elif step == 'B':
        return 'H'
    else:
        return step


def errorAndExit():
    print('Invalid file or file not found\n\nUsage : trucks.py path/to/file')
    exit(1)


if len(sys.argv) < 2:
    errorAndExit()

filePath = sys.argv[1]

if not os.path.exists(filePath):
    errorAndExit()

with open(filePath, 'r') as file:
    # Read only the first line
    data = file.readline()

    # Support unsupported stuff anyway
    if ';' in data:
        data = data.split(';')[1]

    rawRoute = data.split(',')

    # Sanitize
    rawRoute = [x.replace('\n', '') for x in rawRoute]
    route = list(filter(lambda x: len(x) == 1 and isValid(x), rawRoute))

    # Extract infos
    loadedSteps = len(route)

    # Get the full route
    route = route + [flipStep(x) for x in route[::-1]]

    # Get the total consumption
    consuptionSteps = [getConsumption(x, i < loadedSteps)
                       for i, x in enumerate(route)]

    totalConsumption = sum(consuptionSteps)

    # Get the barrel count, if needed
    barrels = max(ceil((totalConsumption - STARTING_FUEL) / BARREL_FUEL), 0)

    # Output
    print(
        f'Consumption steps : {["%.2f"%item for item in consuptionSteps]}\n' +
        f'Barrel used : {barrels}\n' +
        f'Total KMs : {len(route)*100}\n' +
        f'Total Consumed L : {totalConsumption:.4f}\n' +
        f'Remaining L : {(barrels*BARREL_FUEL) + STARTING_FUEL - totalConsumption:.4f}\n' +
        f'Execution time (sec.) : {time.time() - START_TIME}')
