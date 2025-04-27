import pandas as pd
import numpy as np

# class Peak:
    
#     _peakDuration = 0
#     _peakIntensity = 0
#     _peakCenter = 0
#     _calibratedIntensity = 0
#     _uncalibratedIntensity = 0
#     _internalStandard = 0
#     _yield = 0
    
    
# Finds all of the starts to the peaks

def findPeakStart(Ind):
    for i in range(Ind.size - 1):
        if Ind[i] == 0 and Ind[i+1] == 1:
            Ind[i+1] = 2
    Ind = np.where(Ind == 2, 1, 0)
    return Ind

# Finds all of the ends of the peaks

def findPeakEnd(Ind):
    for i in range(Ind.size - 1):
        if Ind[i] == 1 and Ind[i+1] == 0:
            Ind[i] = 2
    Ind = np.where(Ind == 2, 1, 0)
    return Ind

# Calculates peak duration and intensities

def findPeakIntensities(peakEdges, iso):
    peakIntensities = []
    intensity = 0
    count = 0
    isPeak = False
    
    # iterate thru all peak edges
    for i in range(peakEdges.size):
        # if in a peak, add count to how many points you've been inside and add the intensity
        if isPeak:
            count += 1
            intensity += iso[i]
        
        # if reached the end of the peak, do calculations and set everything back to zero
        if peakEdges[i] == 1 and isPeak:
            avgIntensity = intensity / count
            peakIntensities.append(avgIntensity)
            intensity = 0
            count = 0
            isPeak = False
            continue
        
        # if at start of peak, start counting
        if peakEdges[i] == 1 and not isPeak:
            isPeak = True
            
    peakIntensities = np.array(peakIntensities)
    return peakIntensities

def findNewRows(peakEdges, newRowMol):
    newRowLocs = []
    isPeak = False
    isNewRow = False
    
    for i in range(peakEdges.size):
        if isPeak and newRowMol[i] > np.nanmean(newRowMol) and not isNewRow:
            isNewRow = True
        
        if peakEdges[i] == 1 and isPeak:
            isPeak = False
            newRowLocs.append(isNewRow)
            isNewRow = False
            continue
        
        if peakEdges[i] == 1 and not isPeak:
            isPeak = True
    
    return np.array(newRowLocs)

def findPeakDurations(peakEdges, time):
    peakDurations = []
    isPeak = False
    begin = 0
    end = 0
    duration = 0
    
    # iterate thru peak edges
    for i in range(peakEdges.size):
        # calculate the duration based on begin and end time of the peak
        if peakEdges[i] == 1 and isPeak:
            end = time[i]
            duration = end - begin
            peakDurations.append(duration)
            isPeak = False
            continue
        
        #if at peak start, record begin time
        if peakEdges[i] == 1 and not isPeak:
            begin = time[i]
            isPeak = True
    return peakDurations

# Finds the center of each peak

def getTimesOfPeakCenters(peakEdges, time):
    peakCenters = []
    isPeak = False
    startOfPeakIndex = 0
    
    # iterate thru peak edges
    for i in range(peakEdges.size):
        # if at start of peak, take that index
        if (not isPeak and peakEdges[i] == 1):
            startOfPeakIndex = i
            isPeak = True
            continue
            
        # at end of peak calculate the midpoint
        if(isPeak and peakEdges[i] == 1):
            peakCenter = (time[startOfPeakIndex] + time[i]) / 2
            peakCenters.append(peakCenter)
            isPeak = False
    peakCenters = np.array(peakCenters)
    return peakCenters

# Finds the minimum above a given threshold

def findMinAboveThreshold(arr, threshold):
    filtered = arr[arr > threshold]
    minVal = np.min(filtered)
    return minVal

# Calculates moving average of a data set

def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

# Finds any potential drops that have been merged

def findPotentialMergedDrops(durations):
    meanDuration = np.mean(durations)
    potentialMerged = []
    
    for d in range(len(durations)):
        # if a duration is 1.5x the length of the mean, mark as sus
        if durations[d] >= meanDuration * 1.5:
            potentialMerged.append(d)
    potentialMerged = np.array(potentialMerged)
    return np.array(potentialMerged)

def findPotentialSpikes(durations, intensitiesA, intensitiesB, centers):
    meanDuration = np.mean(durations)
    indList = []
    for i in range(len(durations) - 1, -1, -1):
        # if duration is .55x the length of the mean, mark as sus
        if durations[i] < meanDuration * 0.55:
            indList.append(i)
    # durations = np.delete(durations, indList)
    # intensitiesA = np.delete(intensitiesA, indList)
    # intensitiesB = np.delete(intensitiesB, indList)
    # centersOfRemovedSpikes = centers[indList]
    # centers = np.delete(centers, indList)
    # return durations, intensitiesA, intensitiesB, centers, indList
    indList.sort()
    indList = np.array(indList)
    return indList

def calibrateData(IsoIntensities):
    calibrated = IsoIntensities.copy()
    min = np.min(calibrated)
    for i in range(calibrated.size):
        # subtract the baseline from all vals
        calibrated[i] = calibrated[i] - min
    return calibrated
  
  # OMITTED TIME MUST NOT BE IN MIDST OF PEAK 
  # MAYBE PASS PEAK START AND END TO ENSURE THAT IT IS NOT IN PEAK
            
def omitTimes(time, IsoA, IsoB, intStand, omittedStart, omittedEnd):
    indList = []
    for i in range(time.size - 1, -1, -1):
        # if time is above or below omitted times, omit them
        if time[i] < omittedStart or time[i] > omittedEnd:
            indList.append(i)
            
    # delete from all other data sets
    IsoA = np.delete(IsoA, indList)
    IsoB = np.delete(IsoB, indList)
    intStand = np.delete(intStand, indList)
    time = np.delete(time, indList)
    return time, IsoA, IsoB, intStand

def createListOfWells(newRowLocations, numRows, numColumns, num_droplets):
    wellList = []
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']

    letterIndex = numRows - 1
    wellNumber = numColumns
    
    for i in range(newRowLocations.size):
        
        if newRowLocations[i] and not newRowLocations[i-1] and i > 0:
            # implement what to do when encounter new row
            if letterIndex == 0:
                letterIndex = numRows - 1
            else:
                letterIndex -= 1
            wellNumber = numColumns
            position = letters[letterIndex] + str(wellNumber)
            wellList.append(position)
            continue
        
        if i % num_droplets == 0 and i != 0:
            # after a well, we want to move to the next well
            wellNumber -= 1
        # append to well list and return
        position = letters[letterIndex] + str(wellNumber)
        wellList.append(position)
        
    return np.array(wellList)
    
    
def deleteRandomNoise(intStandIntensities, durations, centers, AIntensities, BIntensities):
    indList = []
    for i in range(len(durations) - 1, -1, -1):
        if intStandIntensities[i] == 0:
            indList.append(i)
    intStandIntensities = np.delete(intStandIntensities, indList)
    durations = np.delete(durations, indList)
    AIntensities = np.delete(AIntensities, indList)
    BIntensities = np.delete(BIntensities, indList)
    centers = np.delete(centers, indList)
    return intStandIntensities, durations, centers, AIntensities, BIntensities

def createHeatmapArray(calibrated_intensity, rows, cols, num_droplets):
    calibrated_intensity[:] = calibrated_intensity[::-1]
    intensity_per_well = []
    row = []
    for i, intensity in enumerate(calibrated_intensity):
        
        if (i % num_droplets == 1):
            row.append(intensity)
            
        if (i % (cols * num_droplets) == cols * num_droplets - 1):
            intensity_per_well.append(row)
            row = []
    intensity_per_well = list(map(list, zip(*intensity_per_well)))

    return intensity_per_well