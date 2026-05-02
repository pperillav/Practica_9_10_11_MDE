"""
Model exported as python.
Name : modelo
Group : 
With QGIS : 34406
"""

from typing import Any, Optional

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingContext
from qgis.core import QgsProcessingFeedback, QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterRasterDestination
from qgis import processing


class Modelo(QgsProcessingAlgorithm):

    def initAlgorithm(self, config: Optional[dict[str, Any]] = None):
        # Modelo Digital de Elevacion
        self.addParameter(QgsProcessingParameterRasterLayer('dem_crudo', 'DEM CRUDO', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('TriFinal', 'TRI FINAL', createByDefault=True, defaultValue='C:/Users/LAPTOP/OneDrive/Documentos/CAPAS HIDRO GEOMATICA GENERAL/Proyecto Geomatica/TRI DATOS/DATOS TRI.tif'))
        self.addParameter(QgsProcessingParameterRasterDestination('AspectoFinal', 'Aspecto Final', createByDefault=True, defaultValue='C:/Users/LAPTOP/OneDrive/Documentos/CAPAS HIDRO GEOMATICA GENERAL/Proyecto Geomatica/Aspecto/Aspecto.tif'))
        self.addParameter(QgsProcessingParameterRasterDestination('Dem_fill', 'DEM_fill', optional=True, createByDefault=True, defaultValue='C:/Users/LAPTOP/OneDrive/Documentos/CAPAS HIDRO GEOMATICA GENERAL/Proyecto Geomatica/Datos DEM FILL/Datos Dem Fill.tif'))
        self.addParameter(QgsProcessingParameterRasterDestination('PendienteFinal', 'Pendiente Final', createByDefault=True, defaultValue='C:/Users/LAPTOP/OneDrive/Documentos/CAPAS HIDRO GEOMATICA GENERAL/Proyecto Geomatica/Pendiente/Pendiente.tif'))

    def processAlgorithm(self, parameters: dict[str, Any], context: QgsProcessingContext, model_feedback: QgsProcessingFeedback) -> dict[str, Any]:
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # Fill sinks (Wang & Liu)
        alg_params = {
            'BAND': 1,
            'CREATION_OPTIONS': None,
            'INPUT': parameters['dem_crudo'],
            'MIN_SLOPE': 0.01,
            'OUTPUT_FILLED_DEM': parameters['Dem_fill']
        }
        outputs['FillSinksWangLiu'] = processing.run('native:fillsinkswangliu', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Dem_fill'] = outputs['FillSinksWangLiu']['OUTPUT_FILLED_DEM']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Índice de irregularidad del terreno (TRI)
        alg_params = {
            'BAND': 1,
            'COMPUTE_EDGES': False,
            'CREATION_OPTIONS': None,
            'INPUT': outputs['FillSinksWangLiu']['OUTPUT_FILLED_DEM'],
            'OUTPUT': parameters['TriFinal']
        }
        outputs['NdiceDeIrregularidadDelTerrenoTri'] = processing.run('gdal:triterrainruggednessindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['TriFinal'] = outputs['NdiceDeIrregularidadDelTerrenoTri']['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Pendiente
        alg_params = {
            'INPUT': outputs['FillSinksWangLiu']['OUTPUT_FILLED_DEM'],
            'Z_FACTOR': 1,
            'OUTPUT': parameters['PendienteFinal']
        }
        outputs['Pendiente'] = processing.run('native:slope', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PendienteFinal'] = outputs['Pendiente']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Aspecto
        alg_params = {
            'INPUT': outputs['FillSinksWangLiu']['OUTPUT_FILLED_DEM'],
            'Z_FACTOR': 1,
            'OUTPUT': parameters['AspectoFinal']
        }
        outputs['Aspecto'] = processing.run('native:aspect', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['AspectoFinal'] = outputs['Aspecto']['OUTPUT']
        return results

    def name(self) -> str:
        return 'modelo'

    def displayName(self) -> str:
        return 'modelo'

    def group(self) -> str:
        return ''

    def groupId(self) -> str:
        return ''

    def createInstance(self):
        return self.__class__()
