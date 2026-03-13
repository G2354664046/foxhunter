import pefile
import numpy as np
from skimage.feature import hog


def _binary_to_grayscale(file_path: str) -> np.ndarray:
    """Convert raw binary to square grayscale image array."""
    with open(file_path, "rb") as f:
        data = f.read()
    arr = np.frombuffer(data, dtype=np.uint8)
    size = int(np.ceil(np.sqrt(arr.size)))
    padded = np.zeros(size * size, dtype=np.uint8)
    padded[: arr.size] = arr
    image = padded.reshape((size, size))
    return image


def extract_pe_features(file_path: str) -> dict:
    """
    Extract static features from PE file using pefile library.
    """
    try:
        pe = pefile.PE(file_path)
        
        features = {
            "machine": pe.FILE_HEADER.Machine,
            "number_of_sections": pe.FILE_HEADER.NumberOfSections,
            "time_date_stamp": pe.FILE_HEADER.TimeDateStamp,
            "characteristics": pe.FILE_HEADER.Characteristics,
            "image_base": pe.OPTIONAL_HEADER.ImageBase,
            "section_alignment": pe.OPTIONAL_HEADER.SectionAlignment,
            "file_alignment": pe.OPTIONAL_HEADER.FileAlignment,
            "major_subsystem_version": pe.OPTIONAL_HEADER.MajorSubsystemVersion,
            "size_of_image": pe.OPTIONAL_HEADER.SizeOfImage,
            "size_of_headers": pe.OPTIONAL_HEADER.SizeOfHeaders,
            "subsystem": pe.OPTIONAL_HEADER.Subsystem,
            "dll_characteristics": pe.OPTIONAL_HEADER.DllCharacteristics,
            "size_of_stack_reserve": pe.OPTIONAL_HEADER.SizeOfStackReserve,
            "size_of_heap_reserve": pe.OPTIONAL_HEADER.SizeOfHeapReserve,
            "number_of_rva_and_sizes": pe.OPTIONAL_HEADER.NumberOfRvaAndSizes,
        }
        
        # Section information
        sections = []
        for section in pe.sections:
            sections.append({
                "name": section.Name.decode().rstrip('\x00'),
                "virtual_size": section.Misc_VirtualSize,
                "virtual_address": section.VirtualAddress,
                "size_of_raw_data": section.SizeOfRawData,
                "pointer_to_raw_data": section.PointerToRawData,
                "characteristics": section.Characteristics,
            })
        features["sections"] = sections
        
        # Import table
        imports = []
        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                dll_name = entry.dll.decode() if entry.dll else ""
                functions = [imp.name.decode() if imp.name else str(imp.address) for imp in entry.imports]
                imports.append({"dll": dll_name, "functions": functions})
        features["imports"] = imports
        
        # convert binary to grayscale image and compute HOG descriptors
        try:
            image = _binary_to_grayscale(file_path)
            features["image_shape"] = image.shape
            hog_vector = hog(image, pixels_per_cell=(16, 16), cells_per_block=(2, 2), feature_vector=True)
            features["hog_features"] = hog_vector.tolist()
        except Exception:
            # if image conversion fails we continue without these features
            pass
        
        pe.close()
        return features
        
    except Exception as e:
        raise ValueError(f"Failed to extract PE features: {str(e)}")