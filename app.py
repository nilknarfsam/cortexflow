"""Ponto de entrada do CortexFlow."""

import multiprocessing

from src.ui.main_window import run_app

if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_app()
