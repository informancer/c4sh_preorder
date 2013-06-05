# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PreorderTicket'
        db.create_table('preorder_preorderticket', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('backend_id', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2)),
            ('currency', self.gf('django.db.models.fields.CharField')(default='EUR', max_length=3)),
            ('tax_rate', self.gf('django.db.models.fields.SmallIntegerField')(default=19)),
            ('limit_timespan', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('valid_from', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('valid_until', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('limit_amount', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('limit_amount_user', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_ticket', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('preorder', ['PreorderTicket'])

        # Adding model 'PreorderPosition'
        db.create_table('preorder_preorderposition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('preorder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['preorder.Preorder'])),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['preorder.PreorderTicket'])),
            ('uuid', self.gf('c4sh.preorder.models.UUIDField')(unique=True, max_length=64, blank=True)),
            ('redeemed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('preorder', ['PreorderPosition'])

        # Adding model 'Preorder'
        db.create_table('preorder_preorder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')()),
            ('additional_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('unique_secret', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('cached_sum', self.gf('django.db.models.fields.TextField')()),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('paid_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('paid_via', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
        ))
        db.send_create_signal('preorder', ['Preorder'])

        # Adding model 'GoldenToken'
        db.create_table('preorder_goldentoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('token', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['preorder.PreorderTicket'])),
            ('redeemer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('redeemed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('redeem_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('preorder', ['GoldenToken'])

        # Adding model 'PreorderQuota'
        db.create_table('preorder_preorderquota', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['preorder.PreorderTicket'])),
            ('quota', self.gf('django.db.models.fields.IntegerField')()),
            ('sold', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('preorder', ['PreorderQuota'])

        # Adding M2M table for field positions on 'PreorderQuota'
        db.create_table('preorder_preorderquota_positions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('preorderquota', models.ForeignKey(orm['preorder.preorderquota'], null=False)),
            ('preorderposition', models.ForeignKey(orm['preorder.preorderposition'], null=False))
        ))
        db.create_unique('preorder_preorderquota_positions', ['preorderquota_id', 'preorderposition_id'])

        # Adding model 'CustomPreorderTicket'
        db.create_table('preorder_custompreorderticket', (
            ('preorderticket_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['preorder.PreorderTicket'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('preorder', ['CustomPreorderTicket'])

        # Adding model 'CustomPreorder'
        db.create_table('preorder_custompreorder', (
            ('preorder_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['preorder.Preorder'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('preorder', ['CustomPreorder'])


    def backwards(self, orm):
        # Deleting model 'PreorderTicket'
        db.delete_table('preorder_preorderticket')

        # Deleting model 'PreorderPosition'
        db.delete_table('preorder_preorderposition')

        # Deleting model 'Preorder'
        db.delete_table('preorder_preorder')

        # Deleting model 'GoldenToken'
        db.delete_table('preorder_goldentoken')

        # Deleting model 'PreorderQuota'
        db.delete_table('preorder_preorderquota')

        # Removing M2M table for field positions on 'PreorderQuota'
        db.delete_table('preorder_preorderquota_positions')

        # Deleting model 'CustomPreorderTicket'
        db.delete_table('preorder_custompreorderticket')

        # Deleting model 'CustomPreorder'
        db.delete_table('preorder_custompreorder')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'preorder.custompreorder': {
            'Meta': {'object_name': 'CustomPreorder', '_ormbases': ['preorder.Preorder']},
            'preorder_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preorder.Preorder']", 'unique': 'True', 'primary_key': 'True'})
        },
        'preorder.custompreorderticket': {
            'Meta': {'ordering': "['active', 'name', '-price']", 'object_name': 'CustomPreorderTicket', '_ormbases': ['preorder.PreorderTicket']},
            'preorderticket_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preorder.PreorderTicket']", 'unique': 'True', 'primary_key': 'True'})
        },
        'preorder.goldentoken': {
            'Meta': {'object_name': 'GoldenToken'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redeem_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'redeemed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'redeemer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['preorder.PreorderTicket']"}),
            'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'preorder.preorder': {
            'Meta': {'object_name': 'Preorder'},
            'additional_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cached_sum': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'paid_via': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'unique_secret': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'preorder.preorderposition': {
            'Meta': {'object_name': 'PreorderPosition'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preorder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['preorder.Preorder']"}),
            'redeemed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['preorder.PreorderTicket']"}),
            'uuid': ('c4sh.preorder.models.UUIDField', [], {'unique': 'True', 'max_length': '64', 'blank': 'True'})
        },
        'preorder.preorderquota': {
            'Meta': {'object_name': 'PreorderQuota'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'positions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['preorder.PreorderPosition']", 'null': 'True', 'blank': 'True'}),
            'quota': ('django.db.models.fields.IntegerField', [], {}),
            'sold': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['preorder.PreorderTicket']"})
        },
        'preorder.preorderticket': {
            'Meta': {'ordering': "['active', 'name', '-price']", 'object_name': 'PreorderTicket'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'backend_id': ('django.db.models.fields.SmallIntegerField', [], {}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_ticket': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'limit_amount': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'limit_amount_user': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'limit_timespan': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'tax_rate': ('django.db.models.fields.SmallIntegerField', [], {'default': '19'}),
            'valid_from': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'valid_until': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['preorder']