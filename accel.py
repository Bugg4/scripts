#!/usr/bin/env python3

# original at https://gist.github.com/yinonburgansky/7be4d0489a0df8c06a923240b8eb0191
# modified for ease of use in Hyprland

# calculation are based on http://www.esreality.com/index.php?a=post&id=1945096
# assuming windows 10 uses the same calculation as windows 7.
# guesses have been made calculation is not accurate
# touchpad users make sure your touchpad is calibrated with `sudo libinput measure touchpad-size`

import struct
import argparse
import sys
import subprocess as sp
import matplotlib.pyplot as plt  # Uncommented for graphing


def float16x16(num):
    """
    Converts a 64-bit binary string representing a 16.16 fixed-point number
    into a floating-point number.
    """
    return struct.unpack("<i", num[:-4])[0] / int(0xFFFF)


def find2points(x):
    """
    Finds the two control points in the 'points' list that
    surround a given x-value for interpolation.
    """
    i = 0
    while i < len(points) - 2 and x >= points[i + 1][0]:
        i += 1
    # Assert to ensure x is within the bounds of the selected segment
    assert (
        -1e6 + points[i][0] <= x <= points[i + 1][0] + 1e6
    ), f"{points[i][0]} <= {x} <= {points[i+1][0]}"
    return points[i], points[i + 1]


def interpolate(x):
    """
    Performs linear interpolation between two points to find the y-value
    corresponding to a given x-value.
    """
    (x0, y0), (x1, y1) = find2points(x)
    # Avoid division by zero if x0 == x1 (shouldn't happen with well-defined points)
    if x1 - x0 == 0:
        return y0
    return ((x - x0) * y1 + (x1 - x) * y0) / (x1 - x0)


def sample_points(count):
    """
    Generates a specified number of sample points along the acceleration curve
    for use in Hyprland's custom acceleration profile.
    """
    last_point = -2  # Index of the second to last control point
    max_x = points[last_point][0]  # Maximum x-value for sampling
    step = max_x / (count + last_point)  # Calculate the step size for x-values
    sample_points_x = [si * step for si in range(count)]  # Generate x-coordinates
    sample_points_y = [
        interpolate(x) for x in sample_points_x
    ]  # Interpolate y-coordinates
    return sample_points_x, sample_points_y


def hyprctlkw(device_name, option, arg):
    """
    Constructs a hyprctl keyword command string.
    """
    return f"hyprctl keyword device[{device_name}]:{option} {arg}"


if __name__ == "__main__":

    # ===== PARAMETERS =====
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--device-dpi", default=1000, type=int, help="DPI of your mouse device."
    )
    parser.add_argument(
        "--screen-dpi",
        default=96,
        type=int,
        help="Screen DPI. You can calculate this using online tools like sven.de/dpi/.",
    )
    parser.add_argument(
        "--screen-scaling-factor",
        default=1,
        type=float,
        help="Hyprland's screen scaling factor. Note: 1 here often feels more accurate even if Hyprland scaling is set to 1.5. This might require experimentation.",
    )
    parser.add_argument(
        "--sample-point-count",
        default=20,
        type=int,
        help="Number of sample points to generate for the custom acceleration curve.",
    )
    parser.add_argument(
        "--device-name",
        default=None,
        type=str,
        help="Name of your mouse device. Run 'hyprctl devices', look for the 'mice' section, and find the name of your mouse (e.g., 'Logitech G203 LIGHTSYNC Gaming Mouse').",
    )
    parser.add_argument(
        "--sensitivity-factor",
        default=6,
        type=int,
        choices=range(1, 12),
        help=f"""Sensitivity factor translation table for Windows' slider notches:
    1 = 0.1
    2 = 0.2
    3 = 0.4
    4 = 0.6
    5 = 0.8
    6 = 1.0 <- default
    7 = 1.2
    8 = 1.4
    9 = 1.6
    10 = 1.8
    11 = 2.0
        """,
    )

    args = parser.parse_args()

    # TODO: find accurate formulas for scale x and scale y
    # mouse speed: inch/s to device-units/millisecond
    scale_x = args.device_dpi / 1000
    # pointer speed: inch/s to screen pixels/millisecond
    # The sensitivity_factor is applied here as a multiplier to the Y-axis scaling.
    scale_y = (
        (args.screen_dpi / 1000) / args.screen_scaling_factor * args.sensitivity_factor
    )

    # ===== VALUES EXTRACTED FROM WIN 10 REGISTRY =====
    # These are the raw binary values from HKEY_CURRENT_USER\Control Panel\Mouse\SmoothMouseXCurve
    X = [
        b"\x00\x00\x00\x00\x00\x00\x00\x00",
        b"\x15\x6e\x00\x00\x00\x00\x00\x00",
        b"\x00\x40\x01\x00\x00\x00\x00\x00",
        b"\x29\xdc\x03\x00\x00\x00\x00\x00",
        b"\x00\x00\x28\x00\x00\x00\x00\x00",
    ]

    # These are the raw binary values from HKEY_CURRENT_USER\Control Panel\Mouse\SmoothMouseYCurve
    Y = [
        b"\x00\x00\x00\x00\x00\x00\x00\x00",
        b"\xfd\x11\x01\x00\x00\x00\x00\x00",
        b"\x00\x24\x04\x00\x00\x00\x00\x00",
        b"\x00\xfc\x12\x00\x00\x00\x00\x00",
        b"\x00\xc0\xbb\x01\x00\x00\x00\x00",
    ]

    # Convert raw binary values to floating-point numbers and store as [x, y] pairs
    windows_points = [[float16x16(x), float16x16(y)] for x, y in zip(X, Y)]

    # Scale Windows points according to device and screen configuration
    points = [[x * scale_x, y * scale_y] for x, y in windows_points]

    # Generate sample points for the custom acceleration profile
    sample_points_x, sample_points_y = sample_points(args.sample_point_count)

    # Calculate the step for Hyprland's custom acceleration profile
    step = sample_points_x[1] - sample_points_x[0]
    # Format sample points into a space-separated string for Hyprland
    sample_points_str = " ".join(["%.3f" % number for number in sample_points_y])

    if args.device_name:
        # Construct and run hyprctl commands to apply the acceleration profile
        cmds = [
            hyprctlkw(
                args.device_name, "accel_profile", f"custom {step} {sample_points_str}"
            ),
            # Note: scroll_points might not be directly related to mouse acceleration,
            # but is included here as per original script's intent.
            hyprctlkw(
                args.device_name, "scroll_points", f"custom {step} {sample_points_str}"
            ),
        ]

        for c in cmds:
            print(f"Running: {c}")
            sp.run(c, shell=True)
            # os.system(c) # os.system is generally less safe than subprocess.run

        # Print the Hyprland configuration snippet for user's reference
        print(
            f"""
# automatically generated by {" ".join(sys.argv)}
device {{
    name = {args.device_name}
    sensitivity = {args.sensitivity_factor}
    accel_profile = custom {step} {sample_points_str}
    scroll_points =  custom {step} {sample_points_str}
}}
    """
        )

    # ===== GRAPHING =====
    plt.plot(*list(zip(*windows_points)), label=f"windows points")
    plt.plot(*list(zip(*points)), label=f"scaled points")
    plt.xlabel("device-speed")
    plt.ylabel("pointer-speed")
    plt.legend(loc="best")
    plt.show()
    exit()
