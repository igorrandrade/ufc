"""Executa todas as etapas locais e interrompe se os testes falharem."""
import contextlib, io, json, platform, unittest
from datetime import datetime, timezone
from importlib.metadata import version
from .pipeline import ROOT, build
from .analytics import run as analytics
from .inference import run as inference
from .visuals import build as visuals

def main():
    stages = [('coleta e KPIs', build), ('modelo', analytics), ('inferência complementar', inference), ('visualizações e conclusão', visuals)]
    for label, action in stages:
        with contextlib.redirect_stdout(io.StringIO()): action()
        print('Concluído:', label)
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    evidence = {'executed_at':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),
        'packages':{p:version(p) for p in ['numpy','pandas','scikit-learn','scipy','matplotlib','ipython']},
        'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
        'scope':'Execução local. Não comprova execução no Colab hospedado nem conferência dos campos no UFCStats.'}
    (ROOT/'outputs/execution_validation.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
    if not result.wasSuccessful(): raise SystemExit('Testes falharam; verificar resultados.')
    print('Pipeline completo. Abra docs/index.html.')

if __name__ == '__main__': main()
