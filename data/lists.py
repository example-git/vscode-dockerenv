#lists for cleaning up raw text
badstarts = ("[", "\n", "{", "=====", "Guild:", "Channel:", "Topic:", "{Attachments}", "e!", "{Reactions}", "```", "$m")

badcontains = ["https://images-ext-1.discordapp.net/external/",
                "https://media.discordapp.net/attachments/997610545798729748/",
                "https://cdn.discordapp.com/attachments/997610545798729748/"]

replace = "( \([0-9]+\):)"
replace2 = "(\([0-9]+\):)"

#lists for text generation censorship/etc
link = "(http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"

endinglist = ['! ', '. ', '???? ', '.... ', '... ', '? ', '!!!! ', '!!! ', '.. ',
                '???? ', '.. ', '?? ', '!! ', '!??\r\n', '!?\r\n', '!\r\n', '.\r\n', '????\r\n', '....\r\n',
                '...\r\n', '?\r\n']

punctuation = ['!', '.', '?', ':', '(', ')', '<', '>', '[', ']']

replacements = {
    '<@791687453156179999>': '<@677614885349097483>',
    '<@175411535357673473>': '<@1001745147110899722>',
    'nigger': 'nikker',
    'nigga': 'nikka',
    'kill yourself': 'krill urself',
    '$face': '\r\nnikker detected:',
    'niger': 'niker'
    }
