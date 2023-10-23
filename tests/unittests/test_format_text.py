import unittest
import random

from utils.text import augmented_texts_generator, capitalize

class TestFormatText(unittest.TestCase):

    def test_augmentation(self):

        keep_specials = False

        for itest, (text, normalized_text, maximum) in enumerate([
            (
                "[Alison Jordy:] Tu me fais rire [LAUGHTER]. Je chante [SINGING]? [claude-marie JR Michel:] Il y a un bruit [NOISE], je l'ai dit à [PII]. [Alison Jordy:] Ah",
                "[Alison Jordy:] Tu me fais rire [rire]. Je chante ? [Claude-Marie JR Michel:] Il y a un bruit [bruit], je l'ai dit à [Nom]. [Alison Jordy:] Ah" if keep_specials else\
                "[Alison Jordy:] Tu me fais rire. Je chante ? [Claude-Marie JR Michel:] Il y a un bruit, je l'ai dit à Ted. [Alison Jordy:] Ah",
                6 if keep_specials else 5,
            ),
            (
                "[Alison Jordy:] Tu me fais rire. Je chante ? [claude-marie JR Michel:] Il y a un bruit, je l'ai dit à Ted. [Alison Jordy:] Ah",
                "[Alison Jordy:] Tu me fais rire. Je chante ? [Claude-Marie JR Michel:] Il y a un bruit, je l'ai dit à Ted. [Alison Jordy:] Ah",
                5,
            ),
            (
                "[speaker001:] Tu me fais rire [LAUGHTER]. Je chante [SINGING]? [speaker002:] Il y a un bruit [NOISE], je l'ai dit à [PII]. [speaker001:] Ah",
                "[Intervenant 1:] Tu me fais rire [rire]. Je chante ? [Intervenant 2:] Il y a un bruit [bruit], je l'ai dit à [Nom]. [Intervenant 1:] Ah" if keep_specials else\
                "[Intervenant 1:] Tu me fais rire. Je chante ? [Intervenant 2:] Il y a un bruit, je l'ai dit à Ted. [Intervenant 1:] Ah",
                6 if keep_specials else 5,
            ),
            (
                "[speaker001:] Tu me fais rire Je chante [SINGING] [speaker002:] Il y a un bruit je l'ai dit à Ted [speaker001:] Ah",
                "[Intervenant 1:] Tu me fais rire Je chante [Intervenant 2:] Il y a un bruit je l'ai dit à Ted [Intervenant 1:] Ah",
                3,
            ),
            (
                "[speaker001:] tu me fais rire. je chante [SINGING] ? [speaker002:] il y a un bruit, je l'ai dit à ted [speaker001:] ah",
                "[Intervenant 1:] tu me fais rire. je chante ? [Intervenant 2:] il y a un bruit, je l'ai dit à ted [Intervenant 1:] ah",
                3,
            ),
            (
                "[speaker001:] tu me fais rire je chante [SINGING] [speaker002:] il y a un bruit je l'ai dit à ted [speaker001:] ah",
                "[Intervenant 1:] tu me fais rire je chante [Intervenant 2:] il y a un bruit je l'ai dit à ted [Intervenant 1:] ah",
                1,
            ),
        ]):

            random.seed(51)
            all_variants = list(augmented_texts_generator(text, None))
            self.assertEqual(len(all_variants)-1, maximum, msg=f"\n{itest=}")  # Expected number of generated text

            for level in 5, 4, 3, 2, 1, 0:

                # Note: Ted is the one generated by names with the seed used below
                extreme_normalization = r"[Intervenant 1:] tu me fais rire je chante [Intervenant 2:] il y a un bruit je l'ai dit à ted [Intervenant 1:] ah"
                
                random.seed(51)
                augmented_texts = list(augmented_texts_generator(text, level))
                msg_augmented_texts= '\n  * '.join(augmented_texts)
                msg = f"\n{itest=}\n{level=}\n{maximum=}\n{text=}\naugmented_texts:\n  * {msg_augmented_texts}"
                self.assertEqual(len(augmented_texts), min(maximum+1, level+1), msg=msg)    # Expected number of generated text
                self.assertEqual(len(augmented_texts), len(set(augmented_texts)), msg=msg)  # All generated texts are different
                self.assertEqual(augmented_texts[0], normalized_text, msg=msg)              # First text is the normalized text
                if level >= maximum:
                    # The deepest normalization is always in
                    self.assertTrue(extreme_normalization in augmented_texts, msg=msg + f"\nNOT FOUND: \"{extreme_normalization}\"")
                for t in augmented_texts:
                    self.assertTrue(t in all_variants, msg=msg + f"\nNOT FOUND: \"{t}\"") # All generated texts are in the list of all variants

            found_augmented = False
            for i in range(10):
                augmented_texts = list(augmented_texts_generator(text, 0, force_augmentation=True))
                self.assertEqual(len(augmented_texts), 1)                                   # Only one text is generated
                if augmented_texts[0] != normalized_text:
                    found_augmented = True
                    break
            self.assertTrue(found_augmented, msg=msg)                                          # The generated text can be different than the (normalized) text

        # Check unanomization (sometimes first names alone, sometimes first and last names)
        text = "[speaker001:] A [speaker002:] B [speaker001:] C [speaker003:] D [speaker002:] E [speaker003:] F [speaker001:] G"
        random.seed(123)

        augmented_texts = []
        for i in range(3):
            augmented_texts += augmented_texts_generator(text, 4)

        # print(sorted(list(set(augmented_texts))))
        self.assertEqual(
            sorted(list(set(augmented_texts))),
            ['[Elizabeth Neal:] A [Susan Davis:] B [Elizabeth Neal:] C [Michael Rottenberg:] D [Susan Davis:] E [Michael Rottenberg:] F [Elizabeth Neal:] G',
             '[Elizabeth Neal:] a [Susan Davis:] b [Elizabeth Neal:] c [Michael Rottenberg:] d [Susan Davis:] e [Michael Rottenberg:] f [Elizabeth Neal:] g',
             '[Intervenant 1:] A [Intervenant 2:] B [Intervenant 1:] C [Intervenant 3:] D [Intervenant 2:] E [Intervenant 3:] F [Intervenant 1:] G',
             '[Intervenant 1:] a [Intervenant 2:] b [Intervenant 1:] c [Intervenant 3:] d [Intervenant 2:] e [Intervenant 3:] f [Intervenant 1:] g',
             '[Jerome:] A [Margaret:] B [Jerome:] C [Kevin:] D [Margaret:] E [Kevin:] F [Jerome:] G',
             '[Jerome:] a [Margaret:] b [Jerome:] c [Kevin:] d [Margaret:] e [Kevin:] f [Jerome:] g',
             '[William:] A [April:] B [William:] C [William:] D [April:] E [William:] F [William:] G',
             '[William:] a [April:] b [William:] c [William:] d [April:] e [William:] f [William:] g']
        )

    def test_capitalize(self):

        self.assertEqual(
            capitalize("jean Jean JEAN JR jean-claude Jean-Claude d'estaing D'Estaing"),
            "Jean Jean Jean JR Jean-Claude Jean-Claude D'Estaing D'Estaing"
        )

    def test_remove_empty_turns(self):

        text = "[speaker001:] Je veux dire que Jean-Paul [speaker002:] [rire] [speaker001:] que tu ne peux pas [speaker002:] que je ne peux pas ?... [speaker001:] te moquer de moi comme ça! [spkeaker002:] ... [speaker001:] Bah oui [speaker002:] ..."
        normed_text = self.normalize_text(text)
        self.assertEqual(normed_text,
            "[Intervenant 1:] Je veux dire que Jean-Paul que tu ne peux pas [Intervenant 2:] que je ne peux pas ?... [Intervenant 1:] te moquer de moi comme ça! Bah oui [Intervenant 2:] ...")

        text = "[speaker001:] Je veux dire que Jean-Paul\n[speaker002:] [rire]\n[speaker001:] que tu ne peux pas\n[speaker002:] que je ne peux pas ?...\n[speaker001:] te moquer de moi comme ça!\n[spkeaker002:] ...\n[speaker001:] Bah oui\n[speaker002:] ..."
        normed_text = self.normalize_text(text)
        self.assertEqual(normed_text,
            "[Intervenant 1:] Je veux dire que Jean-Paul que tu ne peux pas\n[Intervenant 2:] que je ne peux pas ?...\n[Intervenant 1:] te moquer de moi comme ça! Bah oui\n[Intervenant 2:] ...")

        text = "[M. Jean-Marie:] Hey [Dr. Docteur JR:] Ow [M. Jean-Marie:] [blah]. [M. Hide:] Hey [M. Jean-Marie:] [re] [m. hide:] Ow"
        normed_text = self.normalize_text(text)
        self.assertEqual(normed_text,
            "[M. Jean-Marie:] Hey [Dr. Docteur JR:] Ow [M. Hide:] Hey Ow"
        )

        text = "[M. Jean-Marie:] Hey\n[Dr. Docteur JR:] Ow\n[M. Jean-Marie:] [blah].\n[M. Hide:] Hey\n[M. Jean-Marie:] [re]\n[m. hide:] Ow"
        normed_text = self.normalize_text(text)
        self.assertEqual(normed_text,
            "[M. Jean-Marie:] Hey\n[Dr. Docteur JR:] Ow\n[M. Hide:] Hey Ow"
        )

    def normalize_text(self, text):
        return list(augmented_texts_generator(text, 0))[0]