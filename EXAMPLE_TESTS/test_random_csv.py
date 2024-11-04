import os
import csv
import random
from pathlib import Path

def maintest(settings, test_series, plot_function, *args, **kwargs):
    # Generate 50 random values
    random_values = [random.uniform(0, 100) for _ in range(50)]

    # Save to CSV in the data directory
    working_dir = Path(settings['working_directory'])
    data_dir = working_dir
    csv_path = data_dir / 'random_values.csv'

    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Random Value'])
        for value in random_values:
            writer.writerow([value])

    print(f"CSV file saved to: {csv_path}")

    # Calculate sum of random values
    total_sum = sum(random_values)

    # Write report to output directory
    output_dir = Path(settings['output_directory'])
    report_path = output_dir/'report.txt'


    with open(report_path, 'w') as reportfile:
        reportfile.write(f"Sum of 50 random values: {total_sum}\n")

    print(f"Report file saved to: {report_path}")

    return "pass"