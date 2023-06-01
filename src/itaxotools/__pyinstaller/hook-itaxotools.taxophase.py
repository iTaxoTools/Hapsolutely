from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('itaxotools.convphase_gui')

hiddenimports = collect_submodules(
    'itaxotools.convphase_gui.task', filter=lambda name: True)
