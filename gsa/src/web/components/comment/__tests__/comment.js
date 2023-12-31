/* Copyright (C) 2019-2022 Greenbone AG
 *
 * SPDX-License-Identifier: AGPL-3.0-or-later
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Affero General Public License
 * as published by the Free Software Foundation, either version 3
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

import React from 'react';

import {render} from 'web/utils/testing';

import Comment from '../comment';

describe('Comment tests', () => {
  test('should render comment', () => {
    const {element} = render(<Comment />);

    expect(element).toMatchSnapshot();
  });

  test('should render children', () => {
    const {element} = render(<Comment>Hello World</Comment>);

    expect(element).toHaveTextContent('Hello World');
  });

  test('should render comment with text', () => {
    const {element} = render(
      <Comment text="Hello World">Should not be rendered</Comment>,
    );

    expect(element).toHaveTextContent('Hello World');
  });
});
