import os
from pathlib import Path
from PIL import Image
import io


class GestorFirmas:
    """Gestiona el almacenamiento y recuperación de firmas."""

    CARPETA_FIRMAS = "firmas"

    def __init__(self):
        self._crear_carpeta_firmas()

    def _crear_carpeta_firmas(self) -> None:
        """Crea la carpeta de firmas si no existe."""
        Path(self.CARPETA_FIRMAS).mkdir(exist_ok=True)

    def guardar_firma(self, canvas_result, firma_id: str) -> bool:
        """Guarda una firma desde un canvas de Streamlit.
        
        Args:
            canvas_result: Resultado del st_canvas de streamlit_drawable_canvas
            firma_id: Identificador único para la firma (ej: fecha_hora_ingreso)
        
        Returns:
            bool: True si se guardó exitosamente, False si no hay contenido o error
        """
        try:
            if canvas_result.image_data is None:
                return False
            
            imagen = Image.fromarray(canvas_result.image_data.astype("uint8"), "RGBA")
            ruta_firma = os.path.join(self.CARPETA_FIRMAS, f"{firma_id}.png")
            imagen.save(ruta_firma)
            return True
        except Exception as e:
            print(f"Error al guardar firma: {str(e)}")
            return False

    def obtener_ruta_firma(self, firma_id: str) -> str:
        """Obtiene la ruta completa de una firma guardada.
        
        Args:
            firma_id: Identificador único de la firma
        
        Returns:
            str: Ruta completa del archivo de firma
        """
        return os.path.join(self.CARPETA_FIRMAS, f"{firma_id}.png")

    def firma_existe(self, firma_id: str) -> bool:
        """Verifica si una firma existe.
        
        Args:
            firma_id: Identificador único de la firma
        
        Returns:
            bool: True si la firma existe, False en caso contrario
        """
        return os.path.exists(self.obtener_ruta_firma(firma_id))

    def obtener_imagen_firma(self, firma_id: str) -> Image.Image or None:
        """Obtiene una firma como objeto Image de PIL.
        
        Args:
            firma_id: Identificador único de la firma
        
        Returns:
            Image.Image o None: La imagen de la firma o None si no existe
        """
        ruta = self.obtener_ruta_firma(firma_id)
        if os.path.exists(ruta):
            return Image.open(ruta)
        return None

    def eliminar_firma(self, firma_id: str) -> bool:
        """Elimina una firma guardada.
        
        Args:
            firma_id: Identificador único de la firma
        
        Returns:
            bool: True si se eliminó, False si no existe
        """
        ruta = self.obtener_ruta_firma(firma_id)
        if os.path.exists(ruta):
            try:
                os.remove(ruta)
                return True
            except Exception as e:
                print(f"Error al eliminar firma: {str(e)}")
                return False
        return False
