import matchering as mg

class MasteringEngine:
    def process(self, target_path, reference_path, output_path):
        try:
            mg.process(
                target=target_path,
                reference=reference_path,
                results=[mg.pcm16(output_path)],
                config=mg.Config(max_length=15 * 60) # 15 min limit
            )
            return True, "Mastering Complete"
        except Exception as e:
            return False, str(e)
