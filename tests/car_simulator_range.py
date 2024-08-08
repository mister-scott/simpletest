import time
import os
import pandas as pd
from pathlib import Path

def maintest(settings, test_series, plot_function, **kwargs):
    # Extract test parameters from kwargs
    recording_count = kwargs.get('recording_count', 1)
    snapshot_count = kwargs.get('snapshot_count', 1)
    capture_delay = kwargs.get('capture_delay', 1)
    road_type = kwargs.get('road_type', 'asphalt')
    start_velocity = kwargs.get('start_velocity', 0)
    end_velocity = kwargs.get('end_velocity', 100)
    velocity_step = kwargs.get('velocity_step', 10)
    start_speedbump_frequency = kwargs.get('start_speedbump_frequency', 0)
    end_speedbump_frequency = kwargs.get('end_speedbump_frequency', 10)
    speedbump_frequency_step = kwargs.get('speedbump_frequency_step', 1)
    fuel_level_threshold = kwargs.get('fuel_level_threshold', 10.0)

    # Initialize car and instrument
    if not initialize_car() or not initialize_instrument():
        print("Failed to initialize car or instrument")
        return "fail"

    # Set road type
    if not set_roadtype(road_type):
        print(f"Failed to set road type to {road_type}")
        return "fail"

    # Create directories for saving data
    working_dir = Path(settings['working_directory'])
    recordings_dir = working_dir / 'recordings'
    snapshots_dir = working_dir / 'snapshots'
    recordings_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    for speedbump_freq in range(start_speedbump_frequency, end_speedbump_frequency + 1, speedbump_frequency_step):
        # Start car
        start_car()

        # Set speedbump frequency
        if not set_speedbump_frequency(speedbump_freq):
            print(f"Failed to set speedbump frequency to {speedbump_freq}")
            stop_car()
            return "fail"

        for velocity in range(start_velocity, end_velocity + 1, velocity_step):
            # Set velocity
            if not set_velocity(velocity):
                print(f"Failed to set velocity to {velocity}")
                stop_car()
                return "fail"

            # Check velocity
            actual_velocity = get_velocity()
            tolerance = max(0.01 * velocity, 10)
            if abs(actual_velocity - velocity) > tolerance:
                print(f"Velocity out of range: set {velocity}, actual {actual_velocity}")
                stop_car()
                return "fail"

            # Check fuel level
            if get_fuel_level() < fuel_level_threshold:
                print(f"Fuel level below threshold: {get_fuel_level()} < {fuel_level_threshold}")
                stop_car()
                return "fail"

            for iteration in range(1, max(recording_count, snapshot_count) + 1):
                # Delay
                time.sleep(capture_delay)

                # Recording
                if iteration <= recording_count:
                    prepare_car_recording()
                    prepare_instrument_recording()
                    trigger_recording()
                    car_recording = get_car_recording()
                    instrument_recording = get_instrument_recording()

                    # Save recordings
                    save_dataframe(car_recording, recordings_dir / f'iteration_{iteration}' / 'car', 
                                   f'{road_type}_{velocity}_{speedbump_freq}_car.csv')
                    save_dataframe(instrument_recording, recordings_dir / f'iteration_{iteration}' / 'instrument', 
                                   f'{road_type}_{velocity}_{speedbump_freq}_instrument.csv')

                # Snapshots
                if iteration <= snapshot_count:
                    car_snapshot = get_car_snapshot()
                    instrument_snapshot = get_instrument_snapshot()

                    # Save snapshots
                    save_dict(car_snapshot, snapshots_dir / f'iteration_{iteration}' / 'car', 
                              f'{road_type}_{velocity}_{speedbump_freq}_car.csv')
                    save_dict(instrument_snapshot, snapshots_dir / f'iteration_{iteration}' / 'instrument', 
                              f'{road_type}_{velocity}_{speedbump_freq}_instrument.csv')

        # Stop car after each speedbump frequency iteration
        stop_car()

    return "pass"

def save_dataframe(df, directory, filename):
    directory.mkdir(parents=True, exist_ok=True)
    df.to_csv(directory / filename, index=False)

def save_dict(data, directory, filename):
    directory.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([data]).to_csv(directory / filename, index=False)