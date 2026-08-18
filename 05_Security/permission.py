from __future__ import annotations
class PermissionManager:
    SAFE_INTENTS={"open","search","close","chat","remember","recall","hud"}
    def allowed(self,intent): return intent in self.SAFE_INTENTS
    def confirm(self,action): return True
