# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Data marshalling utilities for ArrowTable protobufs, which are used by
CustomComponent for dataframe serialization.
"""

import pandas as pd

from streamlit import type_util
from streamlit.elements.lib import pandas_styler_utils


def marshall(proto, data, default_uuid=None):
    """Marshall data into an ArrowTable proto.

    Parameters
    ----------
    proto : proto.ArrowTable
        Output. The protobuf for a Streamlit ArrowTable proto.

    data : pandas.DataFrame, pandas.Styler, numpy.ndarray, Iterable, dict, or None
        Something that is or can be converted to a dataframe.

    """
    if type_util.is_pandas_styler(data):
        pandas_styler_utils.marshall_styler(proto, data, default_uuid)

    df = type_util.convert_anything_to_df(data)
    _marshall_index(proto, df.index)
    _marshall_columns(proto, df.columns)
    _marshall_data(proto, df)


def _marshall_index(proto, index):
    """Marshall pandas.DataFrame index into an ArrowTable proto.

    Parameters
    ----------
    proto : proto.ArrowTable
        Output. The protobuf for a Streamlit ArrowTable proto.

    index : Index or array-like
        Index to use for resulting frame.
        Will default to RangeIndex (0, 1, 2, ..., n) if no index is provided.

    """
    index = map(type_util.maybe_tuple_to_list, index.values)
    index_df = pd.DataFrame(index)
    proto.index = type_util.data_frame_to_bytes(index_df)


def _marshall_columns(proto, columns):
    """Marshall pandas.DataFrame columns into an ArrowTable proto.

    Parameters
    ----------
    proto : proto.ArrowTable
        Output. The protobuf for a Streamlit ArrowTable proto.

    columns : Index or array-like
        Column labels to use for resulting frame.
        Will default to RangeIndex (0, 1, 2, ..., n) if no column labels are provided.

    """
    columns = map(type_util.maybe_tuple_to_list, columns.values)
    columns_df = pd.DataFrame(columns)
    proto.columns = type_util.data_frame_to_bytes(columns_df)


def _marshall_data(proto, df):
    """Marshall pandas.DataFrame data into an ArrowTable proto.

    Parameters
    ----------
    proto : proto.ArrowTable
        Output. The protobuf for a Streamlit ArrowTable proto.

    df : pandas.DataFrame
        A dataframe to marshall.

    """
    proto.data = type_util.serialize_anything_to_arrow_ipc(df)


def arrow_proto_to_dataframe(proto):
    """Convert ArrowTable proto to pandas.DataFrame.

    Parameters
    ----------
    proto : proto.ArrowTable
        Output. pandas.DataFrame

    """
    data = type_util.bytes_to_data_frame(proto.data)
    index = type_util.bytes_to_data_frame(proto.index)
    columns = type_util.bytes_to_data_frame(proto.columns)

    return pd.DataFrame(
        data.values, index=index.values.T.tolist(), columns=columns.values.T.tolist()
    )
