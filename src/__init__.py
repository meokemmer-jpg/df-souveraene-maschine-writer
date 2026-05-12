"""df-souveraene-maschine-writer src package [CRUX-MK]"""
__version__ = "0.1.0-skeleton"


def __getattr__(name):
    if name in ("ChapterGenerator", "OutlineManager", "StyleGuide",
                "AdapterOrchestrator", "AuditLogger", "Chapter",
                "GeneratedChapter", "OrchestratorRunResult"):
        from . import all_modules
        return getattr(all_modules, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
