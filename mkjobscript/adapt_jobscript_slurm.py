#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import re
import sys


def _srun_set_flag(line, flag, value):
    """Replace or append a -flag value pair in a srun command line."""
    value_str = f".{'true' if value else 'false'}." if isinstance(value, bool) else str(value)
    updated = re.sub(
        r'(-' + re.escape(flag) + r'\s+)\S+',
        lambda m: m.group(1) + value_str,
        line,
    )
    if updated == line:  # flag not present, append it
        updated = line.rstrip('\n') + f' -{flag} {value_str}\n'
    return updated


def adapt_jobscript_slurm(
    cmd_nodes=None,
    cmd_ntasks_per_node=None,
    cmd_n_modeltasks=None,
    cmd_filtertype=None,
    cmd_subtype=None,
    cmd_delt_obs=None,
    cmd_rms_obs=None,
    cmd_obs_file=None,
    cmd_use_omi=None,
    cmd_screen=None,
    cmd_forget=None,
    cmd_locweight=None,
    cmd_cradius=None,
    cmd_sradius=None,
):
    with open("jobscript.slurm", "r") as f:
        lines = f.readlines()

    modified_lines = []
    for line in lines:
        if line.startswith("#SBATCH --nodes=") and cmd_nodes is not None:
            modified_lines.append(f"#SBATCH --nodes={cmd_nodes}\n")
        elif line.startswith("#SBATCH --ntasks-per-node=") and cmd_ntasks_per_node is not None:
            modified_lines.append(f"#SBATCH --ntasks-per-node={cmd_ntasks_per_node}\n")
        elif line.startswith("srun"):
            if cmd_n_modeltasks is not None:
                line = _srun_set_flag(line, "n_modeltasks", cmd_n_modeltasks)
            if cmd_screen is not None:
                line = _srun_set_flag(line, "screen", cmd_screen)
            if cmd_filtertype is not None:
                line = _srun_set_flag(line, "filtertype", cmd_filtertype)
            if cmd_subtype is not None:
                line = _srun_set_flag(line, "subtype", cmd_subtype)
            if cmd_delt_obs is not None:
                line = _srun_set_flag(line, "delt_obs", cmd_delt_obs)
            if cmd_rms_obs is not None:
                line = _srun_set_flag(line, "rms_obs", cmd_rms_obs)
            if cmd_use_omi is not None:
                line = _srun_set_flag(line, "use_omi", cmd_use_omi)
            if cmd_forget is not None:
                line = _srun_set_flag(line, "forget", cmd_forget)
            if cmd_locweight is not None:
                line = _srun_set_flag(line, "locweight", cmd_locweight)
            if cmd_cradius is not None:
                line = _srun_set_flag(line, "cradius", cmd_cradius)
            if cmd_sradius is not None:
                line = _srun_set_flag(line, "sradius", cmd_sradius)
            if cmd_obs_file is not None:
                line = _srun_set_flag(line, "obs_filename", cmd_obs_file)
            modified_lines.append(line)
        else:
            modified_lines.append(line)

    with open("jobscript.slurm", "w") as f:
        f.writelines(modified_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Modify jobscript.slurm for eCLM-PDAF runs"
    )
    parser.add_argument(
        "-r", "--rundir",
        default=".",
        help="Directory containing jobscript.slurm (default: current directory)",
    )

    group_cmd = parser.add_argument_group(
        "CMD",
        "jobscript.slurm command line options — "
        "https://hpscterrsys.github.io/pdaf/users_guide/running_tsmp_pdaf/input_cmd.html",
    )
    group_cmd.add_argument("--cmd-nodes", type=int, default=None,
                           help="Number of nodes (#SBATCH --nodes)")
    group_cmd.add_argument("--cmd-ntasks_per_node", type=int, default=None,
                           help="Number of tasks per node (#SBATCH --ntasks-per-node)")
    group_cmd.add_argument("--cmd-n_modeltasks", type=int, default=None,
                           help="Number of realisations (must equal da-nreal)")
    group_cmd.add_argument("--cmd-filtertype", type=int, default=None,
                           help="Filter type (2: EnKF, 4: ETKF, 5: LETKF, 6: ESTKF, 7: LESTKF, 8: LEnKF)")
    group_cmd.add_argument("--cmd-subtype", type=int, default=None,
                           help="Filter subtype (filter-dependent)")
    group_cmd.add_argument("--cmd-delt_obs", type=int, default=None,
                           help="Number of DA intervals forward-computed before assimilation")
    group_cmd.add_argument("--cmd-rms_obs", type=float, default=None,
                           help="Observation error standard deviation")
    group_cmd.add_argument("--cmd-obs_file", type=str, default=None,
                           help="Observation file path plus stem (-obs_filename)")
    group_cmd.add_argument("--cmd-use_omi", default=None,
                           action=argparse.BooleanOptionalAction,
                           help="Use OMI interface")
    group_cmd.add_argument("--cmd-screen", type=int, default=None,
                           help="PDAF output verbosity (0: none, 1: basic, 2: +timing, 3: +debug)")
    group_cmd.add_argument("--cmd-forget", type=float, default=None,
                           help="Forgetting factor for filter analysis")
    group_cmd.add_argument("--cmd-locweight", type=int, default=None,
                           help="Localization weight function (0: uniform, 1: exponential, 2: Gaspari-Cohn)")
    group_cmd.add_argument("--cmd-cradius", type=float, default=None,
                           help="Cut-off radius for localization")
    group_cmd.add_argument("--cmd-sradius", type=float, default=None,
                           help="Support radius for localization")

    # Check for duplicate flags
    seen_flags = set()
    for token in sys.argv[1:]:
        if token.startswith("-"):
            if token in seen_flags:
                parser.error(f"argument {token} appears more than once")
            seen_flags.add(token)

    args = parser.parse_args()

    os.chdir(args.rundir)

    adapt_jobscript_slurm(**{k: v for k, v in vars(args).items()
                             if k.startswith("cmd_")})
