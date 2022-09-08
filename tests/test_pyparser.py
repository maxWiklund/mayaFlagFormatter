from unittest import TestCase

from mayaff import config, mayaff_api
import textwrap


class TestReformat(TestCase):
    config_cls = config.MayaArgsConfig("2018")

    def test_case1(self):
        source_code = textwrap.dedent(
            """
            from maya import cmds
            f = (
                "hahha"
            )

            cmds.delete(
                source,
                ch=function(hi="help"),
                at =cmds.trim(n = "hello")
            )
        """
        )

        expected_result = textwrap.dedent(
            """
            from maya import cmds
            f = (
                "hahha"
            )

            cmds.delete(
                source,
                constructionHistory=function(hi="help"),
                attribute =cmds.trim(name = "hello")
            )
        """
        )

        self.assertEqual(expected_result, mayaff_api.format_string(source_code, config=self.config_cls))

    def test_single_line_comment(self):
        source_code = textwrap.dedent(
            """
            from maya import cmds
            #cmds.delete(source, ch=function(hi="help"))
            """
        )

        expected_result = textwrap.dedent(
            """
            from maya import cmds
            #cmds.delete(source, ch=function(hi="help"))
            """
        )

        self.assertEqual(expected_result, mayaff_api.format_string(source_code, config=self.config_cls))

    def test_nested_single_line_comment(self):
        source_code = textwrap.dedent(
            """
            from maya import cmds as fgh
            fgh.cMuscleWeightPrune(
                pr=True, # cmds.delete(source, ch=function(hi="help"))
                wt=3
            )
            """
        )

        expected_result = textwrap.dedent(
            """
            from maya import cmds as fgh
            fgh.cMuscleWeightPrune(
                prune=True, # cmds.delete(source, ch=function(hi="help"))
                weight=3
            )
            """
        )

        self.assertEqual(expected_result, mayaff_api.format_string(source_code, config=self.config_cls))

    def test_multi_line_comment(self):
        source_code = textwrap.dedent(
            """
            from maya import cmds
            '''
            #
            cmds.delete(source, ch=function(hi="help"))
            '''
        """
        )

        expected_result = textwrap.dedent(
            """
            from maya import cmds
            '''
            #
            cmds.delete(source, ch=function(hi="help"))
            '''
        """
        )

        self.assertEqual(expected_result, mayaff_api.format_string(source_code, config=self.config_cls))

    def test_import_cmds_as_alias(self):
        source_code = textwrap.dedent(
            """
            import maya.cmds as taco
            taco.textureWindow(source, itn="t")
            """
        )

        expected_result = textwrap.dedent(
            """
            import maya.cmds as taco
            taco.textureWindow(source, imageToTextureNumber="t")
            """
        )

        self.assertEqual(expected_result, mayaff_api.format_string(source_code, config=self.config_cls))

    def test_import_cmds(self):
        source_code = textwrap.dedent(
            """
            import maya.cmds
            from abc import cmds
            cmds.volumeBind(q=True)
            maya.cmds.textureWindow(source, itn="t")
            """
        )

        expected_result = textwrap.dedent(
            """
            import maya.cmds
            from abc import cmds
            cmds.volumeBind(q=True)
            maya.cmds.textureWindow(source, imageToTextureNumber="t")
            """
        )

        self.assertEqual(expected_result, mayaff_api.format_string(source_code, config=self.config_cls))

    def test_backtracking_import(self):
        source_code = textwrap.dedent(
            """
            import maya.asdf
            import maya.cmds
            from abc import cmds
            cmds.volumeBind(q=True)
            maya.cmds.textureWindow(source, ra="t")
            """
        )

        expected_result = textwrap.dedent(
            """
            import maya.asdf
            import maya.cmds
            from abc import cmds
            cmds.volumeBind(q=True)
            maya.cmds.textureWindow(source, removeAllImages="t")
            """
        )

        self.assertEqual(expected_result, mayaff_api.format_string(source_code, config=self.config_cls))

    def test_scope_handeling(self):
        source_code = textwrap.dedent(
            """
            from maya import cmds as abc

            abc.textureWindow(source, ra=(
                abc.about(ppc=True),
                abc.about(li=True),
            ))
            """
        )

        expected_result = textwrap.dedent(
            """
            from maya import cmds as abc

            abc.textureWindow(source, removeAllImages=(
                abc.about(macOSppc=True),
                abc.about(linux=True),
            ))
            """
        )

        self.assertEqual(expected_result, mayaff_api.format_string(source_code, config=self.config_cls))

    def test_parse_python2_raise_exception(self):
        source_code = textwrap.dedent(
            """
            from maya import cmds as abc
            print "hello"

            abc.textureWindow(source, ra=(
                abc.about(ppc=True),
                abc.about(li=True),
            ))
            """
        )
        with self.assertRaises(SyntaxError) as context:
            self.assertRaises(SyntaxError, mayaff_api.format_string(source_code, self.config_cls))

    def test_custom_modules(self):
        source_code = textwrap.dedent(
            """
            from ABC.maya2 import abc

            abc.textureWindow(source, ra=True)
            """
        )

        expected_result = textwrap.dedent(
            """
            from ABC.maya2 import abc

            abc.textureWindow(source, removeAllImages=True)
            """
        )

        _config = config.MayaArgsConfig(modules=[("ABC.maya2", "abc")])

        self.assertEqual(expected_result, mayaff_api.format_string(source_code, config=_config))
