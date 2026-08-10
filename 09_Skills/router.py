class JarvisSkills:

    def handle(self, message):
        message = message.lower().strip()

        # App skill
        if message.startswith("open "):
            return "app", message[5:].strip()

        return None, None