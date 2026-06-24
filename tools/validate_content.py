from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader

registry = ContentLoader(ROOT / "content").load()
if registry.warnings:
    print("Content warnings:")
    for warning in registry.warnings:
        print(f"- {warning}")
    raise SystemExit(1)
print("OK")
print(
    "cards={cards} enemies={enemies} relics={relics} potions={potions} ancients={ancients} events={events}".format(
        cards=len(registry.cards),
        enemies=len(registry.enemies),
        relics=len(registry.relics),
        potions=len(registry.potions),
        ancients=len(registry.ancients),
        events=len(registry.events),
    )
)
