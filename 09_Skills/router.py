class JarvisSkills:

    def handle(self, message):

        # -----------------------------------------
        # CLEAN COMMAND
        # -----------------------------------------

        message = message.lower().strip()

        # Remove punctuation
        message = message.rstrip(".,!?")

        # Allow commands like:
        # "Jarvis, open YouTube"
        # "Jarvis open YouTube"
        if message.startswith("jarvis,"):
            message = message[7:].strip()

        elif message.startswith("jarvis "):
            message = message[7:].strip()


        # -----------------------------------------
        # POLITE COMMAND CLEANUP
        # -----------------------------------------

        polite_prefixes = [
            "please ",
            "can you ",
            "could you ",
            "would you ",
        ]

        for prefix in polite_prefixes:
            if message.startswith(prefix):
                message = message[len(prefix):].strip()
                break


        # -----------------------------------------
        # WEBSITE COMMANDS
        # -----------------------------------------

        websites = {
            "youtube": [
                "open youtube",
                "launch youtube",
                "start youtube",
                "go to youtube",
                "open up youtube",
                "bring up youtube",
            ],

            "google": [
                "open google",
                "launch google",
                "start google",
                "go to google",
                "open up google",
                "bring up google",
            ],

            "spotify": [
                "open spotify",
                "launch spotify",
                "start spotify",
                "go to spotify",
                "open up spotify",
                "bring up spotify",
            ],
        }


        for website, commands in websites.items():

            if message in commands:
                return "browser_open", website


        # -----------------------------------------
        # BROWSER COMMANDS
        # -----------------------------------------

        if message in [
            "open safari",
            "launch safari",
            "start safari",
            "open browser",
            "launch browser",
            "start browser",
        ]:
            return "browser_open", None


        # -----------------------------------------
        # GOOGLE SEARCH
        # -----------------------------------------

        search_prefixes = [
            "search google for ",
            "search google ",
            "search for ",
            "google ",
            "look up ",
            "look for ",
        ]


        for prefix in search_prefixes:

            if message.startswith(prefix):

                query = message[len(prefix):].strip()

                if query:
                    return "browser_search", query


        # -----------------------------------------
        # CLOSE / QUIT APP
        # -----------------------------------------

        close_phrases = [
            "close ",
            "quit ",
            "exit ",
            "shut down ",
        ]


        for phrase in close_phrases:

            if message.startswith(phrase):

                app_name = message[len(phrase):].strip()

                if app_name.endswith(" for me"):
                    app_name = app_name[:-7].strip()

                if app_name.endswith(" please"):
                    app_name = app_name[:-7].strip()

                if app_name:
                    return "close_app", app_name


        # -----------------------------------------
        # APP COMMANDS
        # -----------------------------------------

        app_phrases = [
            "open up ",
            "bring up ",
            "launch ",
            "start ",
            "run ",
            "open ",
        ]


        for phrase in app_phrases:

            if message.startswith(phrase):

                app_name = message[len(phrase):].strip()


                # Remove polite endings
                endings = [
                    " for me",
                    " please",
                ]

                for ending in endings:

                    if app_name.endswith(ending):
                        app_name = app_name[:-len(ending)].strip()


                if app_name:
                    return "app", app_name


        # -----------------------------------------
        # USER JUST SAID "OPEN"
        # -----------------------------------------

        if message in [
            "open",
            "launch",
            "start",
            "run",
        ]:
            return "app_help", None


        # -----------------------------------------
        # NOTHING FOUND
        # -----------------------------------------

        return None, None