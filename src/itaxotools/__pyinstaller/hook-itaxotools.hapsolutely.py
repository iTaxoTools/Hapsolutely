from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files("itaxotools.hapsolutely")

datas += collect_data_files("Bio.Align")
datas += collect_data_files("Bio.Phylo")

hiddenimports = collect_submodules(
    "itaxotools.hapsolutely.tasks", filter=lambda name: True
)
