"""Offline controls; no public announcement is assumed or contacted."""
import html
import importlib.util
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('announcement',HERE/'check_arxiv_announcement.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)


class AnnouncementControls(unittest.TestCase):
    def setUp(self):
        self.local=M.local_metadata((HERE.parents[1]/'paper/main.tex').read_text())
        self.document=''.join(f'<meta name="citation_{k}" content="{html.escape(v,quote=True)}">' for k,v in [
            ('title',self.local['title']),('author',self.local['authors'][0]),('arxiv_id','2611.00001'),
            ('pdf_url','https://arxiv.org/pdf/2611.00001v1')])+f'<blockquote class="abstract mathjax">Abstract: {html.escape(self.local["abstract"])}</blockquote>'
        self.remote=M.remote_metadata(self.document,'2611.00001')

    def compare(self,remote=None,pages=23):
        return M.compare(self.local,remote or self.remote,'2611.00001',1,23,pages)

    def test_matching_fixture(self):
        self.assertEqual(self.compare()['status'],'match')

    def test_arxiv_family_first_names_and_pinned_pdf(self):
        self.assertTrue(self.compare({**self.remote,'authors':['Chen, Yufeiyang']})['checks']['authors'])
        document=self.document.replace('/pdf/2611.00001v1','/pdf/2611.00001')+'arXiv:2611.00001v1 [v1] [v2]'
        parsed=M.remote_metadata(document,'2611.00001')
        self.assertEqual(parsed['version'],1)
        self.assertEqual(parsed['pdf_url'],'https://arxiv.org/pdf/2611.00001v1')

    def test_explicit_short_abstract_keeps_paper_difference_visible(self):
        expected=(HERE/'expected_submission_abstract.txt').read_text().strip()
        remote={**self.remote,'abstract':expected}
        self.assertFalse(self.compare(remote)['checks']['abstract'])
        result=M.compare(self.local,remote,'2611.00001',1,23,23,expected)
        self.assertEqual(result['status'],'match')
        self.assertFalse(result['paper_abstract_matches_public'])
        self.assertTrue(result['paper_abstract_diff'])
        changed={**remote,'abstract':expected+' Unsupported added claim.'}
        self.assertFalse(M.compare(self.local,changed,'2611.00001',1,23,23,expected)['checks']['abstract'])

    def test_submission_number_rejected(self):
        for value in ('submit/8326462','8326462','https://arxiv.org/abs/2611.00001'):
            with self.assertRaises(ValueError):M.identifier(value)

    def test_wrong_title_abstract_author_version_identifier(self):
        replacements={'title':'different title','abstract':'different abstract','authors':['Someone Else'],
                      'version':2,'arxiv_id':'2611.00002'}
        for key,value in replacements.items():
            with self.subTest(key=key):
                self.assertFalse(self.compare({**self.remote,key:value})['checks'][key if key!='arxiv_id' else 'identifier'])

    def test_page_count_mismatch(self):
        self.assertFalse(self.compare(pages=24)['checks']['pdf_pages'])

    def test_missing_identity_is_not_inferred(self):
        with self.assertRaises(ValueError):M.remote_metadata(self.document.replace('citation_arxiv_id','other'),'2611.00001')

    def test_unknown_macro_and_redirect_refused(self):
        with self.assertRaises(ValueError):M.tex_plain('\\unknown{word}')
        with self.assertRaises(ValueError):M.remote_metadata(self.document.replace('https://arxiv.org/pdf/','https://example.com/pdf/'),'2611.00001')


if __name__=='__main__':unittest.main()
