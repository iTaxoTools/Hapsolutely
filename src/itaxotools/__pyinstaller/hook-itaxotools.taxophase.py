from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('itaxotools.taxophase.gui')

datas += collect_data_files('Bio.Align')
datas += collect_data_files('Bio.Phylo')

hiddenimports = collect_submodules(
    'itaxotools.taxophase.gui.task', filter=lambda name: True)
