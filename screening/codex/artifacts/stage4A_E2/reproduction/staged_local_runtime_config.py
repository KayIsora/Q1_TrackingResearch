"""Temporary Stage-4A-E2 paths for the bounded official runner.

This file is staged externally.  It must not be installed into the pinned
SpikeTrack worktree until the acquired OTB layout and the three-sequence
mini-root have been verified.
"""

import os

from lib.test.evaluation.environment import EnvSettings


def local_env_settings():
    settings = EnvSettings()
    settings.prj_dir = r"E:\Robot_Backup\tmp\stage4A_R_official_source"
    settings.save_dir = os.environ["SPIKETRACK_STAGE4A_E2_SAVE_ROOT"]
    settings.results_path = os.path.join(settings.save_dir, "tracking_results")
    settings.segmentation_path = os.path.join(
        settings.save_dir, "segmentation_results"
    )
    settings.network_path = os.path.join(settings.save_dir, "networks")
    settings.result_plot_path = os.path.join(settings.save_dir, "result_plots")
    settings.otb_path = os.environ["SPIKETRACK_STAGE4A_E2_OTB_ROOT"]
    return settings
