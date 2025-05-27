import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
import os


@dataclass
class Peak:
    peak_number: int
    peak_center: float
    duration: float
    isomer_intensities: dict[str, float]
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
        self.df: pd.DataFrame = pd.read_excel(filepath)
        self.df.columns = self.df.columns.str.strip()
        self.time = self.df['Time (min)'].to_numpy()
        self.int_stand = self.df['IS'].to_numpy()
        self.marker = self.df['Marker'].to_numpy()
        
        self.isomer_columns = [col for col in self.df.columns if isinstance(col, str) and col.startswith("Isomer")]
        self.isomer_data = {col: self.df[col].to_numpy() for col in self.isomer_columns}
        
    # get time of peak, peak duration, and intensities
    def process_peaks(self, marker_present: bool) -> None:
        int_stand_mean: float = np.nanmean(self.int_stand)
        if marker_present:
            marker_mean: float = np.nanmean(self.marker)
        peakInd = np.where(self.int_stand > (int_stand_mean / 4), 1, 0)
        count = 0
        internal_standard = 0
        marker = 0
        isomer_sums = {iso: 0 for iso in self.isomer_columns}
        
        for i in range(1, peakInd.size - 1):
            # start of peak
            if peakInd[i] and not peakInd[i - 1]:
                count = 1
                marker = self.marker[i] 
                internal_standard = self.int_stand[i]
                isomer_sums = {iso: self.isomer_data[iso][i] for iso in self.isomer_columns}
            
            # inside of peak
            elif peakInd[i] and peakInd[i - 1]:
                count += 1
                for iso in self.isomer_columns:
                    isomer_sums[iso] += self.isomer_data[iso][i]
                marker += self.marker[i]
                internal_standard += self.int_stand[i]
            
            # end of peak
            if peakInd[i] and not peakInd[i + 1]:
                isomer_means = {iso: val / count for iso, val in isomer_sums.items()}
                mean_int_stand = internal_standard / count
                duration = self.time[i] - self.time[i - count + 1]
                self.num_durations += 1
                self.total_duration += duration
                peak_center = (self.time[i] + self.time[i - count + 1]) / 2
                is_new_row = marker_present and (marker / count) > marker_mean
                peak = Peak(len(self.peaks) + 1, peak_center, duration, isomer_means, mean_int_stand, is_new_row)
                self.peaks.append(peak)
    
    # find potential split or merged peaks
    def find_irregulars(self) -> None:
        mean_duration = self.total_duration / self.num_durations
        for peak in self.peaks:
            if peak.duration > 1.5 * mean_duration:
                self.potential_merged.append(peak.peak_number)
            elif peak.duration < 0.55 * mean_duration:
                self.potential_split.append(peak.peak_number) 
            
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
    
    def write_data(self, folder_path, output_filename):
        data_out = []
        for peak in self.peaks:
            row = {
                "peak_number": peak.peak_number,
                "peak_center": peak.peak_center,
                "duration": peak.duration,
                "well": None,  # filled later
            }
            row.update(peak.isomer_intensities)
            data_out.append(row)

        df_out = pd.DataFrame(data_out)
        df_out[['peak_center', 'duration']] = df_out[['peak_center', 'duration']].round(3)
        for iso in self.isomer_columns:
            df_out[iso] = df_out[iso].round(0)
        padded_list = self.potential_merged + [None] * (len(df_out) - len(self.potential_merged))
        df_out['potential_merged'] = padded_list
        padded_list = self.potential_split + [None] * (len(df_out) - len(self.potential_split))
        df_out['potential_split'] = padded_list
        df_out['well'] = self.well_list
            
        output_filepath = os.path.join(folder_path, output_filename)
        df_out.to_excel(output_filepath, index=False, engine='openpyxl')
        
    def create_heatmap_array(self, rows: int, cols: int, num_droplets: int, iso_name: str) -> list[list[float]]:
        if len(self.peaks) < rows * cols * num_droplets:
            return np.zeros((rows, cols))
        
        self.peaks[:] = self.peaks[::-1]
        intensity_per_well = []
        row = []
        
        for i, peak in enumerate(self.peaks):
            if len(intensity_per_well) == rows:
                return np.array(intensity_per_well)
            
            if (i % num_droplets == 1):
                row.append(peak.isomer_intensities[iso_name])                    
            if (i % (cols * num_droplets) == cols * num_droplets - 1):
                intensity_per_well.append(row)
                row = []
        intensity_per_well = list(map(list, zip(*intensity_per_well)))
        return np.array(intensity_per_well)
        
    def run_all(self, filepath: str, marker_present: bool, num_rows: int, num_cols: int, 
                num_droplets: int, folder_path: str, output_filename: str) -> None:
        self.read_data(filepath)
        self.process_peaks(marker_present)
        self.find_irregulars()
        if marker_present:
            self.create_well_list(num_rows, num_cols, num_droplets)
        self.write_data(folder_path, output_filename)
            