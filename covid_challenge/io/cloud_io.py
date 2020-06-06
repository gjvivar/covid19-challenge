import boto3
import os
import nibabel as nib

from eisen.io import LoadNiftiFromFilename


class LoadS3Nifti(LoadNiftiFromFilename):
    """
    This transform loads Nifti data from the cloud and specifically from S3.

    .. code-block:: python
        from eisen.io import LoadS3Nifti
        tform = LoadS3Nifti(['image', 'label'], 's3://bucket/path/')
    """

    def __init__(self, *args, aws_id=None, aws_secret=None, cache='/cache', **kwargs):
        super(LoadS3Nifti, self).__init__(*args, **kwargs)

        self.cache = cache

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_id,
            aws_secret_access_key=aws_secret
        )

    def __call__(self, data):
        """
        :param data: Data dictionary to be processed by this transform
        :type data: dict
        :return: Updated data dictionary
        :rtype: dict
        """
        for field in self.fields:

            complete_file_path = os.path.join(self.data_dir, data[field])

            without_prefix = complete_file_path[5:]

            broken_down = without_prefix.split('/')

            bucket = broken_down[0]

            object = '/'.join(broken_down[1:])

            filename = os.path.join(self.cache, '-'.join(broken_down[1:]))

            if not os.path.exists(filename):
                for i in range(100):
                    try:
                        self.s3_client.download_file(bucket, object, filename)
                        break
                    except:
                        print('There were problems retrieving the file. Attempt {}'.format(i))

            img = nib.load(filename)

            if self.canonical:
                img = nib.as_closest_canonical(img)

            data[field] = img
            data[field + '_affines'] = img.affine
            data[field + '_orientations'] = nib.aff2axcodes(img.affine)

        return data