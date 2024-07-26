import numpy as np
import scipy

import scipy.integrate
import scipy.interpolate
from scipy.fft import ifft, fftshift
from scipy.constants import pi, c


class PointTarget:
    def __init__(
            self,
            range_to_center,
            target_locations_x,
            target_locations_y,
            target_rcs,
            image_dimensions,
            image_bins,
            azimuth_span,
            initial_frequency,
            bandwidth
    ):
        self.range_to_center   = range_to_center
        self.image_length_x    = image_dimensions[0]
        self.image_length_y    = image_dimensions[1]
        self.image_bins_x      = image_bins[0]
        self.image_bins_y      = image_bins[1]
        self.initial_azimuth   = azimuth_span[0]
        self.final_azimuth     = azimuth_span[1]
        self.bandwidth         = bandwidth
        self.initial_frequency = initial_frequency
        self.wavelength        = c / initial_frequency

        self.target_locations_x = target_locations_x
        self.target_locations_y = target_locations_y
        self.target_rcs = target_rcs

        self._set_range_space()
        self._set_frequency_space()
        self._set_azimuth_space()
        self._set_sensor_positions()
        self._set_k_space()
        self._set_filtered_signal()


    def _set_range_space(self):
        self.diagonal_range  = np.sqrt(self.image_length_x ** 2 + self.image_length_y ** 2)
        self.x = np.linspace(-0.5 * self.image_length_x, 0.5 * self.image_length_x, self.image_bins_x)
        self.y = np.linspace(-0.5 * self.image_length_y, 0.5 * self.image_length_y, self.image_bins_y)
        [self.image_grid_x, self.image_grid_y] = np.meshgrid(self.x, self.y)
        self.image_grid_z = np.zeros(self.image_grid_x.shape)


    def _set_frequency_space(self):
        self.frequency_delta = c / (2 * self.diagonal_range)
        self.num_samples_freq = int(self.bandwidth / self.frequency_delta)
        self.frequencies = np.linspace(
            self.initial_frequency,
            self.initial_frequency + self.bandwidth,
            self.num_samples_freq
        )
        self.wavenumbers = 2 * pi * self.frequencies / c


    def _set_azimuth_space(self):
        self.azimuth_delta = c / (2 * self.diagonal_range * self.initial_frequency)
        self.num_samples_az = int(np.round((self.final_azimuth - self.initial_azimuth) / self.azimuth_delta))
        self.azimuths = np.linspace(self.initial_azimuth, self.final_azimuth, self.num_samples_az)


    def _set_sensor_positions(self):
        self.sensor_x = self.range_to_center * np.cos(np.radians(self.azimuths))
        self.sensor_y = self.range_to_center * np.sin(np.radians(self.azimuths))
        self.sensor_z = np.zeros(self.sensor_x.shape)


    def _set_k_space(self):
        signal = np.zeros((self.num_samples_freq, self.num_samples_az), dtype=complex)
        kx = np.zeros_like(signal)
        ky = np.zeros_like(signal)
        cos_azs = np.cos(np.radians(self.azimuths))
        sin_azs = np.sin(np.radians(self.azimuths))
        k_index = 0
        for azimuth, cos_az, sin_az in zip(self.azimuths, cos_azs, sin_azs):
            line_of_sight = [cos_az, sin_az]
            kx[:, k_index] = self.wavenumbers * cos_az
            ky[:, k_index] = self.wavenumbers * sin_az
            for target_x, target_y, target_rcs in zip(
                self.target_locations_x,
                self.target_locations_y,
                self.target_rcs
            ):
                range_to_target = np.dot(line_of_sight, [target_x, target_y])
                signal[:, k_index] += target_rcs * np.exp(1j * 2 * self.wavenumbers * range_to_target)
            k_index += 1
        self.kx = kx
        self.ky = ky
        self.signal = signal
        self.los_vectors = np.asarray([cos_azs, sin_azs])

    def _set_filtered_signal(self):
        self.filter_coefficients = np.outer(
            np.hamming(self.num_samples_freq),
            np.hamming(self.num_samples_az)
        )
        self.filtered_signal = self.signal * self.filter_coefficients


    def get_backprojection(self, num_pulses: int = 0):
        fft_length = int(8 * np.ceil(np.log2(self.num_samples_freq)))
        range_extent = c / (2 * self.frequency_delta)
        range_window = np.linspace(-0.5 * range_extent, 0.5 * range_extent, fft_length)
        backprojected_image = np.zeros(self.image_grid_x.shape, dtype=complex)
        chirp_rate = 1j * 4 * pi * (1 / self.wavelength)
        if not isinstance(self.range_to_center, list):
            self.range_to_center *= np.ones(len(self.sensor_x))
        index = 0
        for x, y, z in zip(self.sensor_x, self.sensor_y, self.sensor_z):
            range_profile = fftshift(ifft(self.signal[:, index], fft_length))
            range_image = np.sqrt((x - self.image_grid_x)**2 + (y - self.image_grid_y)**2 + (z - self.image_grid_z)**2) - self.range_to_center[index]
            interpolater = scipy.interpolate.interp1d(range_window, range_profile, kind='linear', bounds_error=False, fill_value=0.0)
            backprojected_image += interpolater(range_image) * np.exp(chirp_rate * range_image)
            if num_pulses != 0 and num_pulses == index:
                break
            index += 1
        return backprojected_image