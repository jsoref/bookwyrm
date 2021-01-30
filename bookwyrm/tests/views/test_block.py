''' test for app action functionality '''
from unittest.mock import patch
from django.template.response import TemplateResponse
from django.test import TestCase
from django.test.client import RequestFactory

from bookwyrm import models, views


class BlockViews(TestCase):
    ''' view user and edit profile '''
    def setUp(self):
        ''' we need basic test data and mocks '''
        self.factory = RequestFactory()
        self.local_user = models.User.objects.create_user(
            'mouse@local.com', 'mouse@mouse.mouse', 'password',
            local=True, localname='mouse')
        with patch('bookwyrm.models.user.set_remote_server.delay'):
            self.remote_user = models.User.objects.create_user(
                'rat', 'rat@rat.com', 'ratword',
                local=False,
                remote_id='https://example.com/users/rat',
                inbox='https://example.com/users/rat/inbox',
                outbox='https://example.com/users/rat/outbox',
            )


    def test_block_get(self):
        ''' there are so many views, this just makes sure it LOADS '''
        view = views.Block.as_view()
        request = self.factory.get('')
        request.user = self.local_user
        result = view(request)
        self.assertIsInstance(result, TemplateResponse)
        self.assertEqual(result.template_name, 'preferences/blocks.html')
        self.assertEqual(result.status_code, 200)

    def test_block_post(self):
        ''' create a "block" database entry from an activity '''
        view = views.Block.as_view()
        self.local_user.followers.add(self.remote_user)
        models.UserFollowRequest.objects.create(
            user_subject=self.local_user,
            user_object=self.remote_user)
        self.assertTrue(models.UserFollows.objects.exists())
        self.assertTrue(models.UserFollowRequest.objects.exists())

        request = self.factory.post('')
        request.user = self.local_user
        with patch('bookwyrm.broadcast.broadcast_task.delay'):
            view(request, self.remote_user.id)
        block = models.UserBlocks.objects.get()
        self.assertEqual(block.user_subject, self.local_user)
        self.assertEqual(block.user_object, self.remote_user)

        self.assertFalse(models.UserFollows.objects.exists())
        self.assertFalse(models.UserFollowRequest.objects.exists())

    def test_unblock(self):
        ''' undo a block '''
        self.local_user.blocks.add(self.remote_user)
        request = self.factory.post('')
        request.user = self.local_user

        with patch('bookwyrm.broadcast.broadcast_task.delay'):
            views.block.unblock(request, self.remote_user.id)

        self.assertFalse(models.UserBlocks.objects.exists())