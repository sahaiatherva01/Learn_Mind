# Subject packs loader per Rules.md G.6 and ARCH.md §3
from pathlib import Path
from typing import Any

import yaml


class SubjectPackManager:
    """
    Manages config-driven subject packs.
    Rules.md G.6: Config-driven subject packs (YAML/JSON) instead of hard-coded subject logic.
    """

    def __init__(self, packs_dir: Path | None = None):
        if packs_dir is None:
            packs_dir = Path(__file__).resolve().parents[2] / "seeds" / "subject_packs"
        self.packs_dir = packs_dir
        self._packs: dict[str, dict[str, Any]] = {}
        self._load_all_packs()

    def _load_all_packs(self) -> None:
        if not self.packs_dir.exists():
            return
        for file in self.packs_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(file.read_text(encoding="utf-8"))
                if data and "subject" in data:
                    norm_name = data["subject"].lower()
                    self._packs[norm_name] = data
                    # Also index by code
                    if "code" in data:
                        self._packs[data["code"].lower()] = data
            except Exception as e:
                print(f"Failed to load subject pack {file}: {e}")

    def get_pack(self, subject: str) -> dict[str, Any] | None:
        norm = subject.lower().replace(" ", "_")
        if norm in self._packs:
            return self._packs[norm]
        # Try finding partial match
        for key, pack in self._packs.items():
            if norm in key or key in norm:
                return pack
        return None

    def list_packs(self) -> list[dict[str, Any]]:
        # Return unique packs
        seen = set()
        result = []
        for pack in self._packs.values():
            name = pack.get("subject")
            if name and name not in seen:
                seen.add(name)
                result.append(pack)
        return result

    def get_subject_code(self, subject: str) -> str:
        pack = self.get_pack(subject)
        if pack and "code" in pack:
            return pack["code"]
        # Fallback 3-letter uppercase code
        clean = "".join(c for c in subject if c.isalnum()).upper()
        return (clean[:3] if len(clean) >= 3 else clean.ljust(3, "X"))

    def get_chapter_code(self, subject: str, chapter: str) -> str:
        pack = self.get_pack(subject)
        if pack and "chapters" in pack:
            norm_chap = chapter.lower()
            for ch in pack["chapters"]:
                if ch["name"].lower() in norm_chap or norm_chap in ch["name"].lower():
                    return ch.get("code", "CHP")
        clean = "".join(c for c in chapter if c.isalnum()).upper()
        return (clean[:3] if len(clean) >= 3 else clean.ljust(3, "X"))

    def get_topic_code(self, subject: str, chapter: str, topic: str) -> str:
        pack = self.get_pack(subject)
        if pack and "chapters" in pack:
            norm_chap = chapter.lower()
            norm_top = topic.lower()
            for ch in pack["chapters"]:
                if ch["name"].lower() in norm_chap or norm_chap in ch["name"].lower():
                    for tp in ch.get("topics", []):
                        if tp["name"].lower() in norm_top or norm_top in tp["name"].lower():
                            return tp.get("code", "TOP")
        clean = "".join(c for c in topic if c.isalnum()).upper()
        return (clean[:3] if len(clean) >= 3 else clean.ljust(3, "X"))


subject_pack_manager = SubjectPackManager()
