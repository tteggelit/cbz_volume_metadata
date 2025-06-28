import pathlib
import os
from comicapi.comicarchive import ComicArchive
from comictaggerlib.settings import ComicTaggerSettings
from comicapi.comicarchive import MetaDataStyle

def extract_metadata_from_cbz(file_path):
	settings = ComicTaggerSettings(folder=pathlib.Path(os.path.expanduser("~")) / ".ComicTagger")
	archive = ComicArchive(file_path)

	if not archive.seems_to_be_a_comic_archive():
		print(f"Skipping: {file_path} is not a valid comic archive.")
		return None, None

	if not archive.has_metadata(MetaDataStyle.CIX):
		print(f"No ComicInfo.xml metadata found in {file_path}.")
		return None, None

	metadata = archive.read_metadata(MetaDataStyle.CIX)
	series = metadata.series if metadata.series else None
	volume = metadata.volume if metadata.volume else None
	return series, volume

def update_volume_in_cbz(file_path, new_volume):
	settings = ComicTaggerSettings(folder=pathlib.Path(os.path.expanduser("~")) / ".ComicTagger")
	archive = ComicArchive(file_path)

	if not archive.seems_to_be_a_comic_archive():
		print(f"Skipping: {file_path} is not a valid comic archive.")
		return

	# Read existing metadata or create a new one
	if archive.has_metadata(MetaDataStyle.CIX):
		metadata = archive.read_metadata(MetaDataStyle.CIX)
	else:
		metadata = ComicMetadata()

	old_volume = metadata.volume
	metadata.volume = new_volume

	if old_volume != new_volume:
		success = archive.write_metadata(metadata, MetaDataStyle.CIX)
		if success:
			print(f"✅ Updated {os.path.basename(file_path)}: Volume {old_volume} → {new_volume}")
		else:
			print(f"❌ Failed to update metadata for {file_path}")

def process_cbz_directory(directory, new_volume):
	for filename in os.listdir(directory):
		if filename.lower().endswith(".cbz"):
			file_path = os.path.join(directory, filename)
			series, volume = extract_metadata_from_cbz(file_path)
			series_str = series if series else "Unknown Series"
			volume_str = f"Volume {volume}" if volume else "Volume Not Found"
			print(f"{filename}: {series_str}, {volume_str}")

			if type(new_volume) is int:
				update_volume_in_cbz(file_path, new_volume)
				series, volume = extract_metadata_from_cbz(file_path)
				series_str = series if series else "Unknown Series"
				volume_str = f"Volume {volume}" if volume else "Volume Not Found"
				print(f"{filename}: {series_str}, {volume_str}")

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="Extract series and volume from CBZ files using ComicTagger module.")
	parser.add_argument("directory", help="Path to directory containing CBZ files")
	parser.add_argument("--volume", type=int, help="New volume number to write into each CBZ", required=False)
	args = parser.parse_args()

	if os.path.isdir(args.directory):
		process_cbz_directory(args.directory, args.volume)
	else:
		print(f"Error: '{args.directory}' is not a valid directory.")

