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