import Json.Decode exposing (field, int, string, Decoder)
import Html exposing (text, div, input, button, p, select,label,h1,h2,h3,h4,h5,h6,fieldset, Html)
import Html.Attributes exposing (value,multiple,style)
import Html.Events exposing (onClick, onInput)
import Html exposing (program)
import Http exposing (get, Error, Response, Error(..))
import Task  exposing (Task, succeed, fail, andThen, mapError)   

import Bootstrap.CDN as CDN
import Bootstrap.Grid as Grid
import Bootstrap.Grid.Col as Col
import Bootstrap.Grid.Row as Row 
import Bootstrap.Button as Button
main =
  Html.program
    { init = init 
    , view = view
    , update = update
    , subscriptions = subscriptions
    }

subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none


-- MODEL

type alias Artist =
  { id : String
  , full_name : String
  }

type alias Model =
  { artists : List Artist
  , added: List Artist
  }

model : Model
model =
  { artists=[] 
  , added=[]
  }

init : (Model, Cmd Msg)
init =
  ( model, Cmd.none )

decoder : Decoder (List Artist)
decoder =
    Json.Decode.list artistDecoder

artistDecoder : Decoder Artist
artistDecoder =
    Json.Decode.map2 Artist
        (field "id"  string)
        (field "full_name" string)



-- update

type Msg
  = GetAllArtists
  | AddArtist (Artist)
  | LoadArtists (Result Http.Error (List Artist))


update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  case msg of
    AddArtist artist->
      if (List.member artist model.added) then
        (model, Cmd.none)
      else
        ({model | added=artist::model.added} , Cmd.none)  
        

    GetAllArtists ->
      (model, getAllArtists "")

    LoadArtists (Ok lstArtists) ->
      ( { model | artists=lstArtists }, Cmd.none)

    LoadArtists (Err _) ->
      (model, Cmd.none)

     -- Boilerplate: Mdl action handler.
    

getAllArtists : String -> Cmd Msg
getAllArtists _=
  sendGet LoadArtists ("http://localhost:8887/artists") decoder

sendGet : (Result Error a -> msg) -> String -> Decoder a -> Cmd msg
sendGet msg url decoder =
  Http.get url decoder |> Http.send msg
    


-- VIEW
viewAllArtists: Model -> List (Html Msg)
viewAllArtists model=
  [ div []
    [ h6 [] [text "Artists"]
    , Grid.container []
              (List.map (\artist -> 
                  Grid.row []
                    [ Grid.col [] 
                        [ label [] [ text artist.full_name ]]
                    , Grid.col []
                        [ Button.button 
                          [ Button.roleLink
                          , Button.onClick (AddArtist artist)
                          ] [text "Add"]
                        ]
                    ]
              ) model.artists)
    ]
  ]

viewSelected: List Artist -> List (Html Msg) 
viewSelected artists=
  [ div []
    [ h6 [] [text "Selected"]
    , Grid.container []
              ( List.map (\artist ->
                  Grid.row []
                    [ Grid.col []
                      [ label [] [text artist.full_name]]
                    ]
              ) artists)
    ]
  ]

view : Model -> Html Msg
view model =
  Grid.container []
  [ CDN.stylesheet -- creates an inline style node with the Bootstrap CSS
  , Grid.row []
      [ Grid.col [Col.xs12]
        [ Button.button [Button.primary, Button.onClick GetAllArtists ] [ text "New User" ] ]
      ]
  , Grid.row []
      [ Grid.col [Col.xs6 ]
        (viewAllArtists model)  

      , Grid.col [ Col.xs6]
        (viewSelected model.added)
      ]
  ]