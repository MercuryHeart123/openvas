/* Copyright (C) 2016-2022 Greenbone AG
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
import _ from 'gmp/locale';

import HttpCommand from './http';
import GmpHttp from 'gmp/http/gmp';
class DjangoLoginCommand extends HttpCommand {
    constructor() {
        let httpa = new GmpHttp({ apiServer: '172.31.119.130:8081/api', apiProtocol: 'http' });
        super(httpa);
    }

    login(username, password) {
        return this.httpPost({ username, password }).then(
            response => response.data,
            rej => {
                console.log('django cmd rej ', rej);
                if (rej.isError && rej.isError()) {
                    switch (rej.status) {
                        case 401:
                            rej.setMessage(_('Bad login information'));
                            break;
                        case 404:
                            // likely the config is wrong for the server address
                            rej.setMessage(_('Could not connect to server'));
                            break;
                        case 500:
                            rej.setMessage(_('GMP error during authentication'));
                            break;
                        case 503:
                            rej.setMessage(
                                _(
                                    'The Greenbone Vulnerability Manager service is not ' +
                                    'responding. This could be due to system maintenance. ' +
                                    'Please try again later, check the system status, or ' +
                                    'contact your system administrator.',
                                ),
                            );
                            break;
                        default:
                            break;
                    }
                }
                throw rej;
            },
        );
    }
}
export default DjangoLoginCommand;


// vim: set ts=2 sw=2 tw=80:
