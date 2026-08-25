"""Temporary Stage-4A-R paths for the bounded three-sequence official run."""

import os

from lib.test.evaluation.environment import EnvSettings


def local_env_settings():
    settings = EnvSettings()
    settings.prj_dir = r"E:\Robot_Backup\tmp\stage4A_R_official_source"
    settings.save_dir = os.environ["SPIKETRACK_STAGE4A_R_SAVE_ROOT"]
    settings.results_path = os.path.join(settings.save_dir, "tracking_results")
    settings.segmentation_path = os.path.join(settings.save_dir, "segmentation_results")
    settings.network_path = os.path.join(settings.save_dir, "networks")
    settings.result_plot_path = os.path.join(settings.save_dir, "result_plots")
    settings.otb_path = r"E:\Robot_Backup\tmp\stage4A_R_otb3"
    return settings
