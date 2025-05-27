import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, asdict
import os


@dataclass
class Peak:
    peak_number: int
    peak_center: float
    duration: float
    intensityA: float
    intensityB: float
    internal_standard: float
    is_start_of_row: bool

class DataAnalyzer:
    
    def __init__(self):
        self.peaks: list[Peak] = []
        self.potential_split: list[int] = []
        self.potential_merged: list[int] = []
        
        self.total_duration = 0
        self.num_durations = 0
    
    # read in data from input file
    def read_data(self, filepath: str) -> None:
        self.df: pd.DataFrame = pd.read_excel(filepath, usecols=['Time (min)', 'Isomer 77', 'Isomer 57', 'IS', 'Marker'])
        self.time = self.df['Time (min)'].to_numpy()
        self.isoA = self.df['Isomer 57'].to_numpy()
        self.isoB = self.df['Isomer 77'].to_numpy()
        self.int_stand = self.df['IS'].to_numpy()
        self.marker = self.df['Marker'].to_numpy()
    
    # get time of peak, peak duration, and intensities
    def process_peaks(self, marker_present: bool) -> None:
        int_stand_mean: float = np.nanmean(self.int_stand)
        if marker_present:
            marker_mean: float = np.nanmean(self.marker)
        peakInd = np.where(self.int_stand > (int_stand_mean / 4), 1, 0)
        count = 0
        intensityA = 0
        intensityB = 0
        marker = 0
        
        for i in range(1, peakInd.size - 1):
            # start of peak
            if peakInd[i] and not peakInd[i - 1]:
                count = 1
                marker = self.marker[i]
                intensityA = self.isoA[i]
                intensityB = self.isoB[i]   
                internal_standard = self.int_stand[i]
            
            # inside of peak
            elif peakInd[i] and peakInd[i - 1]:
                count += 1
                marker += self.marker[i]
                intensityA += self.isoA[i]
                intensityB += self.isoB[i]
                internal_standard += self.int_stand[i]
            
            # end of peak
            if peakInd[i] and not peakInd[i + 1]:
                mean_intensity_a = intensityA / count
                mean_intensity_b = intensityB / count
                mean_int_stand = internal_standard / count
                duration = self.time[i] - self.time[i - count + 1]
                self.num_durations += 1
                self.total_duration += duration
                peak_center = (self.time[i] + self.time[i - count + 1]) / 2
                is_new_row = marker_present and (marker / count) > marker_mean
                peak = Peak(len(self.peaks) + 1, peak_center, duration, mean_intensity_a, mean_intensity_b, mean_int_stand, is_new_row)
                self.peaks.append(peak)
    
    # find potential split or merged peaks
    def find_irregulars(self) -> None:
        mean_duration = self.total_duration / self.num_durations
        for peak in self.peaks:
            if peak.duration > 1.5 * mean_duration:
                self.potential_merged.append(peak.peak_number)
            elif peak.duration < 0.55 * mean_duration:
                self.potential_split.append(peak.peak_number)
    
    # calibrate the data with the minimum reading for each isomer            
    def calibrate_data(self) -> None:
        min_intensityA = min(peak.intensityA for peak in self.peaks)
        min_intensityB = min(peak.intensityB for peak in self.peaks)

        for peak in self.peaks:
            peak.intensityA = peak.intensityA - min_intensityA
            peak.intensityB = peak.intensityB - min_intensityB
            
            
    # create well list
    def create_well_list(self, num_rows, num_cols, num_droplets) -> None:
        self.well_list = []
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
        
        letter_index = num_rows - 1
        well_number = num_cols
        
        for i in range(len(self.peaks)):
            
            if i > 0 and self.peaks[i].is_start_of_row and not self.peaks[i-1].is_start_of_row:
                # what to do when encounter new row
                if letter_index == 0:
                    letter_index = num_rows - 1
                else:
                    letter_index -= 1
                well_number = num_cols
                position = letters[letter_index] + str(well_number)
                self.well_list.append(position)
                continue
            
            if i % num_droplets == 0 and i != 0:
                # after a well, we want to move to the next well
                well_number -= 1
                
            position = letters[letter_index] + str(well_number)
            self.well_list.append(position)
    
    # read out data
    
    def write_data(self, selections, folder_path, output_filename):
        
        data_out = [asdict(peak) for peak in self.peaks]

        df_out = pd.DataFrame(data_out)
        df_out.drop(columns=['is_start_of_row'], inplace=True)
        df_out['ratio'] = df_out['intensityA'] / (df_out['intensityA'] + df_out['intensityB'])
        df_out['yield'] = (df_out['intensityA'] + df_out['intensityB']) / df_out['internal_standard']
        df_out['isoA / internal_standard ratio'] = df_out['intensityA'] / df_out['internal_standard']
        df_out['isoB / internal_standard ratio'] = df_out['intensityB'] / df_out['internal_standard']
        df_out = df_out.round(3)
        padded_list = self.potential_merged + [None] * (len(df_out) - len(self.potential_merged))
        df_out['potential_merged'] = padded_list
        padded_list = self.potential_split + [None] * (len(df_out) - len(self.potential_split))
        df_out['potential_split'] = padded_list
        df_out['well'] = self.well_list
        df_out[['intensityA', 'intensityB', 'internal_standard']] = df_out[['intensityA', 'intensityB', 'internal_standard']].round(0)
        labels = ['peak_number', 'peak_center', 'duration', 'intensityA', 'intensityB', 'internal_standard',
                  'ratio', 'yield', 'isoA / internal_standard ratio',
                  'isoB / internal_standard ratio', 'potential_merged', 'potential_split', 'well']

        for i in range(len(selections)):
            df_out.drop(columns=[labels[i]], inplace=True)
            
        output_filepath = os.path.join(folder_path, output_filename)
        df_out.to_excel(output_filepath, index=False, engine='openpyxl')
        
    def create_heatmap_array(self, rows: int, cols: int, num_droplets: int) -> list[list[float]]:
        self.peaks[:] = self.peaks[::-1]
        intensity_per_well = []
        row = []
        for i, peak in enumerate(self.peaks):
            if len(intensity_per_well) == rows:
                return intensity_per_well
            
            if (i % num_droplets == 1):
                row.append(peak.intensityA)                    
            if (i % (cols * num_droplets) == cols * num_droplets - 1):
                intensity_per_well.append(row)
                row = []
        intensity_per_well = list(map(list, zip(*intensity_per_well)))
        return intensity_per_well
        
    def run_all(self, filepath: str, marker_present: bool, num_rows: int, num_cols: int, 
                num_droplets: int, selections: list[int], folder_path: str, output_filename: str) -> None:
        self.read_data(filepath)
        self.process_peaks(marker_present)
        self.find_irregulars()
        self.calibrate_data()
        if marker_present:
            self.create_well_list(num_rows, num_cols, num_droplets)
        self.write_data(selections, folder_path, output_filename)
            