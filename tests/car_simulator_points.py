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
    initial_velocity = kwargs.get('initial_velocity', 0)
    ramp_velocity_step = kwargs.get('ramp_velocity_step', 10)
    fuel_level_threshold = kwargs.get('fuel_level_threshold', 10.0)
    test_conditions = kwargs.get('test_conditions', {})

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

    # Start car
    start_car()

    current_velocity = initial_velocity
    if not set_velocity(current_velocity):
        print(f"Failed to set initial velocity to {current_velocity}")
        stop_car()
        return "fail"

    for condition_index, condition in test_conditions.items():
        target_velocity = condition['velocity']
        target_speedbump_frequency = condition['speedbump_frequency']

        # Ramp velocity
        while current_velocity != target_velocity:
            if current_velocity < target_velocity:
                current_velocity = min(current_velocity + ramp_velocity_step, target_velocity)
            else:
                current_velocity = max(current_velocity - ramp_velocity_step, target_velocity)
            
            if not set_velocity(current_velocity):
                print(f"Failed to set velocity to {current_velocity}")
                stop_car()
                return "fail"
            
            time.sleep(0.1)  # 0.1 second delay between velocity steps

        # Set speedbump frequency
        if not set_speedbump_frequency(target_speedbump_frequency):
            print(f"Failed to set speedbump frequency to {target_speedbump_frequency}")
            stop_car()
            return "fail"

        # Check velocity
        actual_velocity = get_velocity()
        tolerance = max(0.01 * target_velocity, 10)
        if abs(actual_velocity - target_velocity) > tolerance:
            print(f"Velocity out of range: set {target_velocity}, actual {actual_velocity}")
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
                               f'{road_type}_{target_velocity}_{target_speedbump_frequency}_car.csv')
                save_dataframe(instrument_recording, recordings_dir / f'iteration_{iteration}' / 'instrument', 
                               f'{road_type}_{target_velocity}_{target_speedbump_frequency}_instrument.csv')

            # Snapshots
            if iteration <= snapshot_count:
                car_snapshot = get_car_snapshot()
                instrument_snapshot = get_instrument_snapshot()

                # Save snapshots
                save_dict(car_snapshot, snapshots_dir / f'iteration_{iteration}' / 'car', 
                          f'{road_type}_{target_velocity}_{target_speedbump_frequency}_car.csv')
                save_dict(instrument_snapshot, snapshots_dir / f'iteration_{iteration}' / 'instrument', 
                          f'{road_type}_{target_velocity}_{target_speedbump_frequency}_instrument.csv')

    # Stop car after all conditions
    stop_car()

    return "pass"

def save_dataframe(df, directory, filename):
    directory.mkdir(parents=True, exist_ok=True)
    df.to_csv(directory / filename, index=False)

def save_dict(data, directory, filename):
    directory.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([data]).to_csv(directory / filename, index=False)