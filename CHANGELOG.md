# Changelog



## [0.1.0-alpha] - 2025-05-09

### Added
- Initial Instagram Crop Tool with GUI (Tkinter).
- Support for multiple Instagram formats: Feed (4:5), Grid Feed (3:4), Reels (9:16).
- Image preview feature showing original and cropped/split images.
- Feature to split wide/panoramic images into multiple panels (2-5) for Instagram carousels.
- Automatic detection of image width to suggest and limit panel splitting.
- Responsive UI that adapts to window resizing and smaller window sizes.
- Minimum window size to prevent UI breakage.
- Extensive logging for debugging image processing issues.
- Automatic opening of the output directory after processing images.
- Unit tests for core cropping and splitting logic.
- GitHub Actions workflows for:
  - Continuous Integration (running tests on push/pull_request).
  - Automated Releases (building executable and creating GitHub Release on tags).
- `requirements.txt` for managing dependencies.
- This `CHANGELOG.md` file.

### Changed
- Improved UI layout and styling for a more modern look and feel.
- Renamed output filenames to replace colons (`:`) with hyphens (`-`) for better OS compatibility (e.g., `Feed4-5` instead of `Feed4:5`).
- Enhanced error handling during image processing and saving.
- Default Git branch changed from `master` to `main`.

### Fixed
- Issues where output files were 0KB or empty by:
  - Validating image dimensions before saving.
  - Ensuring correct save format based on file extension.
  - Adding quality parameters for JPEG.
  - Handling potential transparency issues by converting to RGB when necessary.
  - Implementing alternative save methods if initial save fails.
- Problem where "Process Image(s)" button sometimes produced no output.
- UI elements (like number of panels radio buttons) being cut off in smaller window sizes.
- File saving issues related to incompatible characters in filenames.

### Removed
- (No major features removed in this initial alpha version)

---