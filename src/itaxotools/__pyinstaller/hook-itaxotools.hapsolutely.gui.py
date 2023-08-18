from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('itaxotools.hapsolutely.gui')

datas += collect_data_files('Bio.Align')
datas += collect_data_files('Bio.Phylo')

hiddenimports = collect_submodules(
    'itaxotools.hapsolutely.gui.tasks', filter=lambda name: True)
